/******************************************************************************
 *
 * Project:  FIT Driver
 * Purpose:  Implement FIT Support - not using the SGI iflFIT library.
 * Author:   Philip Nemec, nemec@keyholecorp.com
 *
 ******************************************************************************
 * Copyright (c) 2001, Keyhole, Inc.
 *
 * SPDX-License-Identifier: MIT
 ****************************************************************************/

#ifndef gstEndian_h_
#define gstEndian_h_

// endian swapping tools

#include <stdio.h>
#include "cpl_port.h"

#include "gstTypes.h"

namespace gstEndian
{

// have to do swapping on Linux and Windows
#ifdef CPL_LSB
#define swapping
#else
#endif

#ifdef swapping
size_t swapped_fread(void *ptr, size_t size, size_t nitems, FILE *stream);
size_t swapped_fwrite(const void *ptr, size_t size, size_t nitems,
                      FILE *stream);

static inline void gst_swap64(void *value)
{
    // 0x1122334455667788 --> 0x8877665544332211

    *(uint64 *)(value) = (((*(uint64 *)(value)&0x00000000000000ff) << 56) |
                          ((*(uint64 *)(value)&0x000000000000ff00) << 40) |
                          ((*(uint64 *)(value)&0x0000000000ff0000) << 24) |
                          ((*(uint64 *)(value)&0x00000000ff000000) << 8) |
                          ((*(uint64 *)(value) >> 8) & 0x00000000ff000000) |
                          ((*(uint64 *)(value) >> 24) & 0x0000000000ff0000) |
                          ((*(uint64 *)(value) >> 40) & 0x000000000000ff00) |
                          ((*(uint64 *)(value) >> 56) & 0x00000000000000ff));
}

static inline void gst_swap32(void *value)
{
    // 0x12 34 56 78 --> 0x78 56 34 12

    *(uint32 *)(value) = (((*(uint32 *)(value)&0x000000ff) << 24) |
                          ((*(uint32 *)(value)&0x0000ff00) << 8) |
                          ((*(uint32 *)(value) >> 8) & 0x0000ff00) |
                          ((*(uint32 *)(value) >> 24) & 0x000000ff));
}

static inline void gst_swap16(void *value)
{
    *(uint16 *)(value) = (((*(uint16 *)(value)&0x00ff) << 8) |
                          ((*(uint16 *)(value) >> 8) & 0x00ff));
}

static inline void gst_swapbytes(void *value, int size)
{
    switch (size)
    {
        case 1:
            // do nothing
            break;
        case 2:
            gst_swap16(value);
            break;
        case 4:
            gst_swap32(value);
            break;
        case 8:
            gst_swap64(value);
            break;
        default:
            fprintf(stderr,
                    "gst_swapbytes unsupported size %i - not swapping\n", size);
            break;
    }  // switch
}

#define gst_swapb(value) gst_swapbytes(&value, sizeof(value))

#else  // swapping

#define swapped_fread(ptr, size, nitems, stream)                               \
    fread(ptr, size, nitems, stream)
#define swapped_fwrite(ptr, size, nitems, stream)                              \
    fwrite(ptr, size, nitems, stream)

#define gst_swap64(value)
#define gst_swap32(value)
#define gst_swap16(value)
#define gst_swapbytes(value, size)
#define gst_swapb(value)

#endif  // swapping

}  // namespace gstEndian

#endif  // ! gstEndian_h_
