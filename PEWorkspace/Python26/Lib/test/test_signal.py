import unittest
from test import test_support
from contextlib import closing, nested
import gc
import pickle
import select
import signal
import subprocess
import traceback
import sys, os, time, errno

if sys.platform[:3] in ('win', 'os2') or sys.platform == 'riscos':
    raise test_support.TestSkipped("Can't test signal on %s" % \
                                   sys.platform)


class HandlerBCalled(Exception):
    pass


def exit_subprocess():
    """Use os._exit(0) to exit the current subprocess.

    Otherwise, the test catches the SystemExit and continues executing
    in parallel with the original test, so you wind up with an
    exponential number of tests running concurrently.
    """
    os._exit(0)


def ignoring_eintr(__func, *args, **kwargs):
    try:
        return __func(*args, **kwargs)
    except EnvironmentError as e:
        if e.errno != errno.EINTR:
            raise
        return None


class InterProcessSignalTests(unittest.TestCase):
    MAX_DURATION = 20   # Entire test should last at most 20 sec.

    def setUp(self):
        self.using_gc = gc.isenabled()
        gc.disable()

    def tearDown(self):
        if self.using_gc:
            gc.enable()

    def format_frame(self, frame, limit=None):
        return ''.join(traceback.format_stack(frame, limit=limit))

    def handlerA(self, signum, frame):
        self.a_called = True
        if test_support.verbose:
            print "handlerA invoked from signal %s at:\n%s" % (
                signum, self.format_frame(frame, limit=1))

    def handlerB(self, signum, frame):
        self.b_called = True
        if test_support.verbose:
            print "handlerB invoked from signal %s at:\n%s" % (
                signum, self.format_frame(frame, limit=1))
        raise HandlerBCalled(signum, self.format_frame(frame))

    def wait(self, child):
        """Wait for child to finish, ignoring EINTR."""
        while True:
            try:
                child.wait()
                return
            except OSError as e:
                if e.errno != errno.EINTR:
                    raise

    def run_test(self):
        # Install handlers. This function runs in a sub-process, so we
        # don't worry about re-setting the default handlers.
        signal.signal(signal.SIGHUP, self.handlerA)
        signal.signal(signal.SIGUSR1, self.handlerB)
        signal.signal(signal.SIGUSR2, signal.SIG_IGN)
        signal.signal(signal.SIGALRM, signal.default_int_handler)

        # Variables the signals will modify:
        self.a_called = False
        self.b_called = False

        # Let the sub-processes know who to send signals to.
        pid = os.getpid()
        if test_support.verbose:
            print "test runner's pid is", pid

        child = ignoring_eintr(subprocess.Popen, ['kill', '-HUP', str(pid)])
        if child:
            self.wait(child)
            if not self.a_called:
                time.sleep(1)  # Give the signal time to be delivered.
        self.assertTrue(self.a_called)
        self.assertFalse(self.b_called)
        self.a_called = False

        # Make sure the signal isn't delivered while the previous
        # Popen object is being destroyed, because __del__ swallows
        # exceptions.
        del child
        try:
            child = subprocess.Popen(['kill', '-USR1', str(pid)])
            # This wait should be interrupted by the signal's exception.
            self.wait(child)
            time.sleep(1)  # Give the signal time to be delivered.
            self.fail('HandlerBCalled exception not thrown')
        except HandlerBCalled:
            self.assertTrue(self.b_called)
            self.assertFalse(self.a_called)
            if test_support.verbose:
                print "HandlerBCalled exception caught"

        child = ignoring_eintr(subprocess.Popen, ['kill', '-USR2', str(pid)])
        if child:
            self.wait(child)  # Nothing should happen.

        try:
            signal.alarm(1)
            # The race condition in pause doesn't matter in this case,
            # since alarm is going to raise a KeyboardException, which
            # will skip the call.
            signal.pause()
            # But if another signal arrives before the alarm, pause
            # may return early.
            time.sleep(1)
        except KeyboardInterrupt:
            if test_support.verbose:
                print "KeyboardInterrupt (the alarm() went off)"
        except:
            self.fail("Some other exception woke us from pause: %s" %
                      traceback.format_exc())
        else:
            self.fail("pause returned of its own accord, and the signal"
                      " didn't arrive after another second.")

    def test_main(self):
        # This function spawns a child process to insulate the main
        # test-running process from all the signals. It then
        # communicates with that child process over a pipe and
        # re-raises information about any exceptions the child
        # throws. The real work happens in self.run_test().
        os_done_r, os_done_w = os.pipe()
        with nested(closing(os.fdopen(os_done_r)),
                    closing(os.fdopen(os_done_w, 'w'))) as (done_r, done_w):
            child = os.fork()
            if child == 0:
                # In the child process; run the test and report results
                # through the pipe.
                try:
                    done_r.close()
                    # Have to close done_w again here because
                    # exit_subprocess() will skip the enclosing with block.
                    with closing(done_w):
                        try:
                            self.run_test()
                        except:
                            pickle.dump(traceback.format_exc(), done_w)
                        else:
                            pickle.dump(None, done_w)
                except:
                    print 'Uh oh, raised from pickle.'
                    traceback.print_exc()
                finally:
                    exit_subprocess()

            done_w.close()
            # Block for up to MAX_DURATION seconds for the test to finish.
            r, w, x = select.select([done_r], [], [], self.MAX_DURATION)
            if done_r in r:
                tb = pickle.load(done_r)
                if tb:
                    self.fail(tb)
            else:
                os.kill(child, signal.SIGKILL)
                self.fail('Test deadlocked after %d seconds.' %
                          self.MAX_DURATION)


class BasicSignalTests(unittest.TestCase):
    def trivial_signal_handler(self, *args):
        pass

    def test_out_of_range_signal_number_raises_error(self):
        self.assertRaises(ValueError, signal.getsignal, 4242)

        self.assertRaises(ValueError, signal.signal, 4242,
                          self.trivial_signal_handler)

    def test_setting_signal_handler_to_none_raises_error(self):
        self.assertRaises(TypeError, signal.signal,
                          signal.SIGUSR1, None)

    def test_getsignal(self):
        hup = signal.signal(signal.SIGHUP, self.trivial_signal_handler)
        self.assertEquals(signal.getsignal(signal.SIGHUP),
                          self.trivial_signal_handler)
        signal.signal(signal.SIGHUP, hup)
        self.assertEquals(signal.getsignal(signal.SIGHUP), hup)


class WakeupSignalTests(unittest.TestCase):
    TIMEOUT_FULL = 10
    TIMEOUT_HALF = 5

    def test_wakeup_fd_early(self):
        import select

        signal.alarm(1)
        before_time = time.time()
        # We attempt to get a signal during the sleep,
        # before select is called
        time.sleep(self.TIMEOUT_FULL)
        mid_time = time.time()
        self.assert_(mid_time - before_time < self.TIMEOUT_HALF)
        select.select([self.read], [], [], self.TIMEOUT_FULL)
        after_time = time.time()
        self.assert_(after_time - mid_time < self.TIMEOUT_HALF)

    def test_wakeup_fd_during(self):
        import select

        signal.alarm(1)
        before_time = time.time()
        # We attempt to get a signal during the select call
        self.assertRaises(select.error, select.select,
            [self.read], [], [], self.TIMEOUT_FULL)
        after_time = time.time()
        self.assert_(after_time - before_time < self.TIMEOUT_HALF)

    def setUp(self):
        import fcntl

        self.alrm = signal.signal(signal.SIGALRM, lambda x,y:None)
        self.read, self.write = os.pipe()
        flags = fcntl.fcntl(self.write, fcntl.F_GETFL, 0)
        flags = flags | os.O_NONBLOCK
        fcntl.fcntl(self.write, fcntl.F_SETFL, flags)
        self.old_wakeup = signal.set_wakeup_fd(self.write)

    def tearDown(self):
        signal.set_wakeup_fd(self.old_wakeup)
        os.close(self.read)
        os.close(self.write)
        signal.signal(signal.SIGALRM, self.alrm)

class SiginterruptTest(unittest.TestCase):
    signum = signal.SIGUSR1
    def readpipe_interrupted(self, cb):
        r, w = os.pipe()
        ppid = os.getpid()
        pid = os.fork()

        oldhandler = signal.signal(self.signum, lambda x,y: None)
        cb()
        if pid==0:
            # child code: sleep, kill, sleep. and then exit,
            # which closes the pipe from which the parent process reads
            try:
                time.sleep(0.2)
                os.kill(ppid, self.signum)
                time.sleep(0.2)
            finally:
                exit_subprocess()

        try:
            os.close(w)

            try:
                d=os.read(r, 1)
                return False
            except OSError, err:
                if err.errno != errno.EINTR:
                    raise
                return True
        finally:
            signal.signal(self.signum, oldhandler)
            os.waitpid(pid, 0)

    def test_without_siginterrupt(self):
        i=self.readpipe_interrupted(lambda: None)
        self.assertEquals(i, True)

    def test_siginterrupt_on(self):
        i=self.readpipe_interrupted(lambda: signal.siginterrupt(self.signum, 1))
        self.assertEquals(i, True)

    def test_siginterrupt_off(self):
        i=self.readpipe_interrupted(lambda: signal.siginterrupt(self.signum, 0))
        self.assertEquals(i, False)

class ItimerTest(unittest.TestCase):
    def setUp(self):
        self.hndl_called = False
        self.hndl_count = 0
        self.itimer = None
        self.old_alarm = signal.signal(signal.SIGALRM, self.sig_alrm)

    def tearDown(self):
        signal.signal(signal.SIGALRM, self.old_alarm)
        if self.itimer is not None: # test_itimer_exc doesn't change this attr
            # just ensure that itimer is stopped
            signal.setitimer(self.itimer, 0)

    def sig_alrm(self, *args):
        self.hndl_called = True
        if test_support.verbose:
            print("SIGALRM handler invoked", args)

    def sig_vtalrm(self, *args):
        self.hndl_called = True

        if self.hndl_count > 3:
            # it shouldn't be here, because it should have been disabled.
            raise signal.ItimerError("setitimer didn't disable ITIMER_VIRTUAL "
                "timer.")
        elif self.hndl_count == 3:
            # disable ITIMER_VIRTUAL, this function shouldn't be called anymore
            signal.setitimer(signal.ITIMER_VIRTUAL, 0)
            if test_support.verbose:
                print("last SIGVTALRM handler call")

        self.hndl_count += 1

        if test_support.verbose:
            print("SIGVTALRM handler invoked", args)

    def sig_prof(self, *args):
        self.hndl_called = True
        signal.setitimer(signal.ITIMER_PROF, 0)

        if test_support.verbose:
            print("SIGPROF handler invoked", args)

    def test_itimer_exc(self):
        # XXX I'm assuming -1 is an invalid itimer, but maybe some platform
        # defines it ?
        self.assertRaises(signal.ItimerError, signal.setitimer, -1, 0)
        # Negative times are treated as zero on some platforms.
        if 0:
            self.assertRaises(signal.ItimerError,
                              signal.setitimer, signal.ITIMER_REAL, -1)

    def test_itimer_real(self):
        self.itimer = signal.ITIMER_REAL
        signal.setitimer(self.itimer, 1.0)
        if test_support.verbose:
            print("\ncall pause()...")
        signal.pause()

        self.assertEqual(self.hndl_called, True)

    def test_itimer_virtual(self):
        self.itimer = signal.ITIMER_VIRTUAL
        signal.signal(signal.SIGVTALRM, self.sig_vtalrm)
        signal.setitimer(self.itimer, 0.3, 0.2)

        for i in xrange(100000000):
            # use up some virtual time by doing real work
            _ = pow(12345, 67890, 10000019)
            if signal.getitimer(self.itimer) == (0.0, 0.0):
                break # sig_vtalrm handler stopped this itimer

        # virtual itimer should be (0.0, 0.0) now
        self.assertEquals(signal.getitimer(self.itimer), (0.0, 0.0))
        # and the handler should have been called
        self.assertEquals(self.hndl_called, True)

    def test_itimer_prof(self):
        self.itimer = signal.ITIMER_PROF
        signal.signal(signal.SIGPROF, self.sig_prof)
        signal.setitimer(self.itimer, 0.2, 0.2)

        for i in xrange(100000000):
            if signal.getitimer(self.itimer) == (0.0, 0.0):
                break # sig_prof handler stopped this itimer

        # profiling itimer should be (0.0, 0.0) now
        self.assertEquals(signal.getitimer(self.itimer), (0.0, 0.0))
        # and the handler should have been called
        self.assertEqual(self.hndl_called, True)

def test_main():
    test_support.run_unittest(BasicSignalTests, InterProcessSignalTests,
        WakeupSignalTests, SiginterruptTest, ItimerTest)


if __name__ == "__main__":
    test_main()
