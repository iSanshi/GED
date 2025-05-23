/*
  zip_set_file_compression.c -- set compression for file in archive
  Copyright (C) 2012 Dieter Baron and Thomas Klausner

  This file is part of libzip, a library to manipulate ZIP archives.
  The authors can be contacted at <libzip@nih.at>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions
  are met:
  1. Redistributions of source code must retain the above copyright
     notice, this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in
     the documentation and/or other materials provided with the
     distribution.
  3. The names of the authors may not be used to endorse or promote
     products derived from this software without specific prior
     written permission.
 
  THIS SOFTWARE IS PROVIDED BY THE AUTHORS ``AS IS'' AND ANY EXPRESS
  OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
  GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
  IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
  IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/



#include "zipint.h"



ZIP_EXTERN int
zip_set_file_compression(struct zip *za, zip_uint64_t idx,
			 zip_int32_t method, zip_uint32_t flags)
{
    struct zip_entry *e;
    zip_int32_t old_method;

    if (idx >= za->nentry) {
	_zip_error_set(&za->error, ZIP_ER_INVAL, 0);
	return -1;
    }

    if (ZIP_IS_RDONLY(za)) {
	_zip_error_set(&za->error, ZIP_ER_RDONLY, 0);
	return -1;
    }

    if (method != ZIP_CM_DEFAULT && method != ZIP_CM_STORE && method != ZIP_CM_DEFLATE) {
	_zip_error_set(&za->error, ZIP_ER_COMPNOTSUPP, 0);
	return -1;
    }

    e = za->entry+idx;
    
    old_method = (e->orig == NULL ? ZIP_CM_DEFAULT : e->orig->comp_method);
    
    /* TODO: revisit this when flags are supported, since they may require a recompression */
    
    if (method == old_method) {
	if (e->changes) {
	    e->changes->changed &= ~ZIP_DIRENT_COMP_METHOD;
	    if (e->changes->changed == 0) {
		_zip_dirent_free(e->changes);
		e->changes = NULL;
	    }
	}
    }
    else {
        if (e->changes == NULL) {
            if ((e->changes=_zip_dirent_clone(e->orig)) == NULL) {
                _zip_error_set(&za->error, ZIP_ER_MEMORY, 0);
                return -1;
            }
        }

        e->changes->comp_method = method;
        e->changes->changed |= ZIP_DIRENT_COMP_METHOD;
    }
    
    return 0;
}
