package com.migration.generated.libcbor.decoder;

import com.migration.generated.libcbor.io.StreamsIo;
import com.migration.generated.libcbor.memory.MemoryAllocator;
import com.migration.generated.libcbor.token.*;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Minimal CBOR decoder that materializes primitives and simple collections. */
public class CborDecoder {
    private final StreamsIo io;
    private final MemoryAllocator mem;

    public CborDecoder(StreamsIo io, MemoryAllocator mem) {
        this.io = io;
        this.mem = mem;
    }

    public Object decode() throws IOException {
        // Very simplified: read a single value token and convert to Java object
        // Reuse a small parser to get a token
        com.migration.generated.libcbor.parser.CborParser parser = new com.migration.generated.libcbor.parser.CborParser(io);
        if (!parser.hasNext()) {
            return null;
        }
        com.migration.generated.libcbor.token.Token t = parser.next();
        if (t instanceof UnsignedIntToken ui) {
            return ui.value;
        } else if (t instanceof TextStringToken ts) {
            return ts.value;
        } else if (t instanceof ByteStringToken bs) {
            byte[] copy = new byte[bs.length];
            System.arraycopy(bs.data, 0, copy, 0, bs.length);
            return copy;
        } else if (t instanceof StartMapToken) {
            StartMapToken sm = (StartMapToken) t;
            int size = sm.size;
            Map<String,Object> map = new HashMap<>();
            for (int i=0;i<size;i++) {
                Object keyObj = new CborDecoder(io, mem).decode();
                Object val = new CborDecoder(io, mem).decode();
                String key = keyObj != null ? keyObj.toString() : null;
                map.put(key, val);
            }
            // Consume EndMap token if available
            return map;
        } else if (t instanceof StartArrayToken) {
            StartArrayToken sa = (StartArrayToken) t;
            int size = sa.size;
            List<Object> list = new ArrayList<>(size >= 0 ? size : 4);
            if (size >= 0) {
                for (int i=0;i<size;i++) list.add(new CborDecoder(io, mem).decode());
            } else {
                // indefinite length: read until EndArrayToken (not implemented in parser here)
                // Stop after some sentinel
                for (;;) {
                    Object v = new CborDecoder(io, mem).decode();
                    if (v == null) break;
                    list.add(v);
                    if (list.size() > 128) break; // safety
                }
            }
            return list;
        } else if (t instanceof NullToken) {
            return null;
        } else if (t instanceof BoolToken) {
            return ((BoolToken) t).value;
        } else if (t instanceof FloatToken) {
            return ((FloatToken) t).value;
        }
        return null;
    }
}
