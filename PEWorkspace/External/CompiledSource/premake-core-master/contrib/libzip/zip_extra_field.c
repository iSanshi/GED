/*
  zip_extra_field.c -- manipulate extra fields
  Copyright (C) 2012-2013 Dieter Baron and Thomas Klausner

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

#include <errno.h>
#include <stdlib.h>
#include <string.h>



struct zip_extra_field *
_zip_ef_clone(const struct zip_extra_field *ef, struct zip_error *error)
{
    struct zip_extra_field *head, *prev, *def;
    
    head = prev = NULL;
    
    while (ef) {
        if ((def=_zip_ef_new(ef->id, ef->size, ef->data, ef->flags)) == NULL) {
            _zip_error_set(error, ZIP_ER_MEMORY, 0);
            _zip_ef_free(head);
            return NULL;
        }
        
        if (head == NULL)
            head = def;
        if (prev)
            prev->next = def;
        prev = def;

	ef = ef->next;
    }
    
    return head;
}


struct zip_extra_field *
_zip_ef_delete_by_id(struct zip_extra_field *ef, zip_uint16_t id, zip_uint16_t id_idx, zip_flags_t flags)
{
    struct zip_extra_field *head, *prev;
    int i;

    i = 0;
    head = ef;
    prev = NULL;
    for (; ef; ef=(prev ? prev->next : head)) {
	if ((ef->flags & flags & ZIP_EF_BOTH) && ((ef->id == id) || (id == ZIP_EXTRA_FIELD_ALL))) {
	    if (id_idx == ZIP_EXTRA_FIELD_ALL || i == id_idx) {
		ef->flags &= ~(flags & ZIP_EF_BOTH);
		if ((ef->flags & ZIP_EF_BOTH) == 0) {
		    if (prev)
			prev->next = ef->next;
		    else
			head = ef->next;
		    ef->next = NULL;
		    _zip_ef_free(ef);

		    if (id_idx == ZIP_EXTRA_FIELD_ALL)
			continue;
		}
	    }
	    
	    i++;
	    if (i > id_idx)
		break;
	}
	prev = ef;
    }

    return head;
}




void
_zip_ef_free(struct zip_extra_field *ef)
{
    struct zip_extra_field *ef2;

    while (ef) {
	ef2 = ef->next;
	free(ef->data);
	free(ef);
	ef = ef2;
    }
}



const zip_uint8_t *
_zip_ef_get_by_id(const struct zip_extra_field *ef, zip_uint16_t *lenp, zip_uint16_t id, zip_uint16_t id_idx, zip_flags_t flags, struct zip_error *error)
{
    static const zip_uint8_t empty[1] = { '\0' };
    
    int i;

    i = 0;
    for (; ef; ef=ef->next) {
	if (ef->id == id && (ef->flags & flags & ZIP_EF_BOTH)) {
	    if (i < id_idx) {
		i++;
		continue;
	    }

	    if (lenp)
		*lenp = ef->size;
	    if (ef->size > 0)
		return ef->data;
	    else
		return empty;
	}
    }

    _zip_error_set(error, ZIP_ER_NOENT, 0);
    return NULL;
}



struct zip_extra_field *
_zip_ef_merge(struct zip_extra_field *to, struct zip_extra_field *from)
{
    struct zip_extra_field *ef2, *tt, *tail;
    int duplicate;

    if (to == NULL)
	return from;

    for (tail=to; tail->next; tail=tail->next)
	;

    for (; from; from=ef2) {
	ef2 = from->next;

	duplicate = 0;
	for (tt=to; tt; tt=tt->next) {
	    if (tt->id == from->id && tt->size == from->size && memcmp(tt->data, from->data, tt->size) == 0) {
		tt->flags |= (from->flags & ZIP_EF_BOTH);
		duplicate = 1;
		break;
	    }
	}

	from->next = NULL;
	if (duplicate)
	    _zip_ef_free(from);
	else
	    tail = tail->next = from;
    }

    return to;
}



struct zip_extra_field *
_zip_ef_new(zip_uint16_t id, zip_uint16_t size, const zip_uint8_t *data, zip_flags_t flags)
{
    struct zip_extra_field *ef;

    if ((ef=(struct zip_extra_field *)malloc(sizeof(*ef))) == NULL)
	return NULL;

    ef->next = NULL;
    ef->flags = flags;
    ef->id = id;
    ef->size = size;
    if (size > 0) {
	if ((ef->data=(zip_uint8_t *)_zip_memdup(data, size, NULL)) == NULL) {
	    free(ef);
	    return NULL;
	}
    }
    else
	ef->data = NULL;

    return ef;
}



struct zip_extra_field *
_zip_ef_parse(const zip_uint8_t *data, zip_uint16_t len, zip_flags_t flags, struct zip_error *error)
{
    struct zip_extra_field *ef, *ef2, *ef_head;
    const zip_uint8_t *p;
    zip_uint16_t fid, flen;

    ef_head = NULL;
    for (p=data; p<data+len; p+=flen) {
	if (p+4 > data+len) {
	    _zip_error_set(error, ZIP_ER_INCONS, 0);
	    _zip_ef_free(ef_head);
	    return NULL;
	}

	fid = _zip_read2(&p);
	flen = _zip_read2(&p);

	if (p+flen > data+len) {
	    _zip_error_set(error, ZIP_ER_INCONS, 0);
	    _zip_ef_free(ef_head);
	    return NULL;
	}

	if ((ef2=_zip_ef_new(fid, flen, p, flags)) == NULL) {
	    _zip_error_set(error, ZIP_ER_MEMORY, 0);
	    _zip_ef_free(ef_head);
	    return NULL;
	}

	if (ef_head) {
	    ef->next = ef2;
	    ef = ef2;
	}
	else
	    ef_head = ef = ef2;
    }

    return ef_head;
}



struct zip_extra_field *
_zip_ef_remove_internal(struct zip_extra_field *ef)
{
    struct zip_extra_field *ef_head;
    struct zip_extra_field *prev, *next;
    
    ef_head = ef;
    prev = NULL;
    
    while (ef) {
        if (ZIP_EF_IS_INTERNAL(ef->id)) {
            next = ef->next;
            if (ef_head == ef)
                ef_head = next;
            ef->next = NULL;
            _zip_ef_free(ef);
            if (prev)
                prev->next = next;
            ef = next;
        }
        else {
            prev = ef;
            ef = ef->next;
        }
    }
    
    return ef_head;
}


zip_uint16_t
_zip_ef_size(const struct zip_extra_field *ef, zip_flags_t flags)
{
    zip_uint16_t size;

    size = 0;
    for (; ef; ef=ef->next) {
	if (ef->flags & flags & ZIP_EF_BOTH)
	    size += 4+ef->size;
    }

    return size;
}



void
_zip_ef_write(const struct zip_extra_field *ef, zip_flags_t flags, FILE *f)
{
    for (; ef; ef=ef->next) {
	if (ef->flags & flags & ZIP_EF_BOTH) {
	    _zip_write2(ef->id, f);
	    _zip_write2(ef->size, f);
	    if (ef->size > 0)
		fwrite(ef->data, ef->size, 1, f);
	}
    }
}



int
_zip_read_local_ef(struct zip *za, zip_uint64_t idx)
{
    struct zip_entry *e;
    unsigned char b[4];
    const unsigned char *p;
    zip_uint16_t fname_len, ef_len;

    if (idx >= za->nentry) {
	_zip_error_set(&za->error, ZIP_ER_INVAL, 0);
	return -1;
    }

    e = za->entry+idx;

    if (e->orig == NULL || e->orig->local_extra_fields_read)
	return 0;


    if (fseeko(za->zp, (off_t)(e->orig->offset + 26), SEEK_SET) < 0) {
	_zip_error_set(&za->error, ZIP_ER_SEEK, errno);
	return -1;
    }

    if (fread(b, sizeof(b), 1, za->zp) != 1) {
	_zip_error_set(&za->error, ZIP_ER_READ, errno);
	return -1;
    }

    p = b;
    fname_len = _zip_read2(&p);
    ef_len = _zip_read2(&p);

    if (ef_len > 0) {
	struct zip_extra_field *ef;
	zip_uint8_t *ef_raw;

	if (fseek(za->zp, fname_len, SEEK_CUR) < 0) {
	    _zip_error_set(&za->error, ZIP_ER_SEEK, errno);
	    return -1;
	}

	ef_raw = _zip_read_data(NULL, za->zp, ef_len, 0, &za->error);

	if (ef_raw == NULL)
	    return -1;

	if ((ef=_zip_ef_parse(ef_raw, ef_len, ZIP_EF_LOCAL, &za->error)) == NULL) {
	    free(ef_raw);
	    return -1;
	}
	free(ef_raw);
	
        ef = _zip_ef_remove_internal(ef);
	e->orig->extra_fields = _zip_ef_merge(e->orig->extra_fields, ef);
    }

    e->orig->local_extra_fields_read = 1;
    
    if (e->changes && e->changes->local_extra_fields_read == 0) {
	e->changes->extra_fields = e->orig->extra_fields;
	e->changes->local_extra_fields_read = 1;
    }

    return 0;
}
