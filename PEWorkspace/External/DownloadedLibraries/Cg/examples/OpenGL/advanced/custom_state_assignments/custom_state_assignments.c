
/* custom_state_assignments - Over-riding pre-defined state assignments and creating new state assignments.  */

#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#ifdef _WIN32
#include <windows.h>
#endif

#include <Cg/cg.h>
#include <Cg/cgGL.h>

static CGcontext   myCgContext;
static CGeffect    myCgEffect;
static CGtechnique myCgTechnique;

static const char *myProgramName = "custom_state_assignments",
                  *myEffectFileName = "custom_sa.cgfx";

static void checkForCgError(const char *situation)
{
  CGerror error;
  const char *string = cgGetLastErrorString(&error);

  if (error != CG_NO_ERROR) {
    printf("%s: %s: %s\n",
      myProgramName, situation, string);
    if (error == CG_COMPILER_ERROR) {
      printf("%s\n", cgGetLastListing(myCgContext));
    }
    exit(1);
  }
}

CGbool program_set( CGstateassignment sa )
{
  printf( "VertexProgram set called.\n" );
  return CG_TRUE;
}

CGbool program_reset( CGstateassignment sa )
{
  printf( "VertexProgram reset called.\n" );
  return CG_TRUE;
}

CGbool program_validate( CGstateassignment sa )
{
  CGprogram prog = cgGetProgramStateAssignmentValue( sa );
  printf( "VertexProgram validate called. - %s\n\n", cgGetProfileString( cgGetProgramProfile( prog ) ) );

  switch( cgGetProgramProfile( prog ) )
  {
    case CG_PROFILE_VS_2_0: return CG_TRUE;
    case CG_PROFILE_ARBVP1: return CG_TRUE; 
    case CG_PROFILE_GLSLV:  return CG_TRUE;
    default:                return CG_FALSE;
  }	
}

CGbool foo_set( CGstateassignment sa )
{
  int nVals = 0;
  const CGbool *val = cgGetBoolStateAssignmentValues( sa, &nVals );
  printf( "\nFooState set called with value %d.\n", *val );
  return CG_TRUE;
}

CGbool foo_reset( CGstateassignment sa )
{
  printf( "\nFooState reset called.\n" );
  return CG_TRUE;
}

CGbool foo_validate( CGstateassignment sa )
{
  printf( "FooState validate called.\n" );
  return CG_TRUE;
}

int main(int argc, char **argv)
{
  CGstate programState, fooState;
  CGpass pass;

  myCgContext = cgCreateContext();
  checkForCgError("creating context");

  cgGLRegisterStates(myCgContext);
  checkForCgError("registering standard CgFX states");

  // Over-ride VertexProgram state assignment that was registered in cgGLRegisterStates(ctx)
  programState = cgGetNamedState( myCgContext, "VertexProgram" );
  cgSetStateCallbacks( programState, program_set, program_reset, program_validate ); 

  // Create and register new state FooState
  fooState = cgCreateState( myCgContext, "FooState", CG_BOOL );
  cgSetStateCallbacks( fooState, foo_set, foo_reset, foo_validate );
  
  myCgEffect = cgCreateEffectFromFile( myCgContext, myEffectFileName, NULL );
  checkForCgError("creating custom_sa.cgfx effect");
  assert(myCgEffect);

  myCgTechnique = cgGetFirstTechnique(myCgEffect);
  while (myCgTechnique && cgValidateTechnique(myCgTechnique) == CG_FALSE) {
    fprintf(stderr, "%s: Technique %s did not validate.  Skipping.\n",
      myProgramName, cgGetTechniqueName(myCgTechnique));
    myCgTechnique = cgGetNextTechnique(myCgTechnique);
  }
  if (myCgTechnique) {
    fprintf(stderr, "%s: Initially using technique %s.\n",
      myProgramName, cgGetTechniqueName(myCgTechnique));
  } else {
    fprintf(stderr, "%s: No valid technique\n",
      myProgramName);
    cgDestroyEffect(myCgEffect);
    cgDestroyContext(myCgContext);
    exit(1);
  }

  // Normally this would be in your render function
  pass = cgGetFirstPass( myCgTechnique );
  while( pass ) 
  {
    cgSetPassState( pass );    
    // draw...
    cgResetPassState( pass );
    pass = cgGetNextPass( pass );
  }

  cgDestroyEffect(myCgEffect);
  cgDestroyContext(myCgContext);
 
  return 0;
}
