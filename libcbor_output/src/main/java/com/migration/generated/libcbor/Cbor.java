package com.migration.generated.libcbor;

import com.migration.generated.libcbor.decoding.CborDecoderResult;
import com.migration.generated.libcbor.decoding.CborDecoderStatus;
import com.migration.generated.libcbor.decoding.CborStreamDecoder;
import com.migration.generated.libcbor.internal.CborBuilderCallbacks;
import com.migration.generated.libcbor.model.CborItem;
import com.migration.generated.libcbor.serialization.CborSerializer;

public final class Cbor {
    private static volatile CborAllocator allocator = CborAllocator.DEFAULT;

    private Cbor() {
    }

    public static CborItem load(byte[] source) {
        LoadResult result = loadPartial(source, 0, source.length);
        if (result.bytesConsumed() != source.length) {
            throw new CborDecodeException("Trailing bytes after top-level CBOR item");
        }
        return result.item();
    }

    public static LoadResult loadPartial(byte[] source, int offset, int length) {
        if (source == null) {
            throw new IllegalArgumentException("Source must not be null");
        }
        if (offset < 0 || length < 0 || offset + length > source.length) {
            throw new IllegalArgumentException("Invalid offset/length range");
        }
        byte[] slice = new byte[length];
        System.arraycopy(source, offset, slice, 0, length);
        CborBuilderCallbacks callbacks = new CborBuilderCallbacks();
        CborDecoderResult result = new CborStreamDecoder().decode(slice, callbacks);
        if (result.status() != CborDecoderStatus.FINISHED) {
            throw new CborDecodeException("Failed to decode CBOR item: " + result.status());
        }
        if (callbacks.rootItem() == null) {
            throw new CborDecodeException("No CBOR item was decoded");
        }
        return new LoadResult(callbacks.rootItem(), result.readCount());
    }

    public static byte[] serialize(CborItem item) {
        byte[] serialized = CborSerializer.serialize(item);
        byte[] allocated = allocator.allocate(serialized.length);
        System.arraycopy(serialized, 0, allocated, 0, serialized.length);
        return allocated;
    }

    public static int serializedSize(CborItem item) {
        return CborSerializer.serializedSize(item);
    }

    public static int serialize(CborItem item, byte[] buffer, int offset) {
        byte[] serialized = CborSerializer.serialize(item);
        if (offset < 0 || offset + serialized.length > buffer.length) {
            throw new IllegalArgumentException("Buffer too small for serialized CBOR item");
        }
        System.arraycopy(serialized, 0, buffer, offset, serialized.length);
        return serialized.length;
    }

    public static CborItem deepCopy(CborItem item) {
        return item.deepCopy();
    }

    public static CborItem deepCopyDefinite(CborItem item) {
        return item.deepCopyDefinite();
    }

    public static boolean structurallyEqual(CborItem left, CborItem right) {
        return left == right || (left != null && left.equals(right));
    }

    public static void describe(CborItem item, Appendable out) {
        CborDescribe.describe(item, out);
    }

    public static String describe(CborItem item) {
        return CborDescribe.describe(item);
    }

    public static void setAllocator(CborAllocator allocator) {
        Cbor.allocator = allocator == null ? CborAllocator.DEFAULT : allocator;
    }
}
