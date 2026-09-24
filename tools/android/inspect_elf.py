#!/usr/bin/env python3
"""Inspect actual ELF headers; file existence alone does not prove an ARM64 .so."""
import struct
from pathlib import Path

def inspect(path):
    path=Path(path);size=path.stat().st_size
    with path.open('rb') as f:
        header=f.read(64)
        if len(header)!=64 or header[:4]!=b'\x7fELF' or header[4:6]!=b'\x02\x01':raise ValueError('Not little-endian ELF64')
        typ,machine=struct.unpack_from('<HH',header,16)
        if typ!=3 or machine!=183:raise ValueError('Not AArch64 ET_DYN')
        phoff=struct.unpack_from('<Q',header,32)[0];phsize,phcount=struct.unpack_from('<HH',header,54)
        if phsize!=56 or not 1<=phcount<=1024 or phoff+phsize*phcount>size:raise ValueError('Invalid program headers')
        f.seek(phoff);loadable=0;dynamic=False
        for _ in range(phcount):
            p=struct.unpack('<IIQQQQQQ',f.read(phsize));kind,offset,filesize=p[0],p[2],p[5]
            if offset+filesize>size:raise ValueError('Truncated ELF segment')
            loadable+=kind==1;dynamic=dynamic or kind==2
        if not loadable or not dynamic:raise ValueError('No load/dynamic segments')
    return {'name':path.name,'bytes':size,'elf_class':64,'machine':'AArch64','type':'shared-object','load_segments':loadable,'headers_and_segment_extents_verified':True}
