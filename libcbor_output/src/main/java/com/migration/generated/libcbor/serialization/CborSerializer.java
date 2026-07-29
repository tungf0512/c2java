package com.migration.generated.libcbor.serialization;

import com.migration.generated.libcbor.CborSerializationException;
import com.migration.generated.libcbor.encoding.CborEncoder;
import com.migration.generated.libcbor.model.*;
import java.io.ByteArrayOutputStream;

public final class CborSerializer {
    private CborSerializer() {
    }

    public static byte[] serialize(CborItem item) {
        ByteArrayOutputStream out = new ByteArrayOutputStream(serializedSize(item));
        write(item, out);
        return out.toByteArray();
    }

    public static int serializedSize(CborItem item) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        write(item, out);
        return out.size();
    }

    private static void write(CborItem item, ByteArrayOutputStream out) {
        if (item instanceof CborUnsignedInteger value) {
            writeUnsignedWithWidth(out, 0, value.value(), value.width());
        } else if (item instanceof CborNegativeInteger value) {
            writeUnsignedWithWidth(out, 1, value.encodedMagnitude(), value.width());
        } else if (item instanceof CborByteString value) {
            if (value.isIndefinite()) {
                out.write(0x5F);
                for (CborByteString chunk : value.chunks()) {
                    write(chunk, out);
                }
                CborEncoder.writeBreak(out);
            } else {
                CborEncoder.writeUnsigned(out, 2, value.bytes().length);
                out.writeBytes(value.bytes());
            }
        } else if (item instanceof CborTextString value) {
            if (value.isIndefinite()) {
                out.write(0x7F);
                for (CborTextString chunk : value.chunks()) {
                    write(chunk, out);
                }
                CborEncoder.writeBreak(out);
            } else {
                byte[] utf8 = value.utf8();
                CborEncoder.writeUnsigned(out, 3, utf8.length);
                out.writeBytes(utf8);
            }
        } else if (item instanceof CborArray value) {
            if (value.isIndefinite()) {
                out.write(0x9F);
                for (CborItem child : value.items()) {
                    write(child, out);
                }
                CborEncoder.writeBreak(out);
            } else {
                CborEncoder.writeUnsigned(out, 4, value.size());
                for (CborItem child : value.items()) {
                    write(child, out);
                }
            }
        } else if (item instanceof CborMap value) {
            if (value.isIndefinite()) {
                out.write(0xBF);
                for (CborPair pair : value.pairs()) {
                    write(pair.key(), out);
                    write(pair.value(), out);
                }
                CborEncoder.writeBreak(out);
            } else {
                CborEncoder.writeUnsigned(out, 5, value.size());
                for (CborPair pair : value.pairs()) {
                    write(pair.key(), out);
                    write(pair.value(), out);
                }
            }
        } else if (item instanceof CborTag value) {
            CborEncoder.writeUnsigned(out, 6, value.value());
            if (value.taggedItem() == null) {
                throw new CborSerializationException("Tag without nested item");
            }
            write(value.taggedItem(), out);
        } else if (item instanceof CborFloatOrCtrl value) {
            switch (value.kind()) {
                case BOOLEAN -> out.write(value.booleanValue() ? 0xF5 : 0xF4);
                case NULL -> out.write(0xF6);
                case UNDEFINED -> out.write(0xF7);
                case BREAK -> out.write(0xFF);
                case SIMPLE -> {
                    long payload = value.payloadBits();
                    if (payload < 24) {
                        out.write((int) (0xE0 | payload));
                    } else {
                        out.write(0xF8);
                        out.write((int) payload);
                    }
                }
                case HALF_FLOAT -> {
                    out.write(0xF9);
                    CborEncoder.writeShort(out, (int) value.payloadBits());
                }
                case SINGLE_FLOAT -> {
                    out.write(0xFA);
                    CborEncoder.writeInt(out, (int) value.payloadBits());
                }
                case DOUBLE_FLOAT -> {
                    out.write(0xFB);
                    CborEncoder.writeLong(out, value.payloadBits());
                }
            }
        } else {
            throw new CborSerializationException("Unsupported CBOR item type: " + item.getClass().getName());
        }
    }

    private static void writeUnsignedWithWidth(ByteArrayOutputStream out, int majorType, long value, CborWidth width) {
        switch (width) {
            case ZERO -> {
                if (value >= 24) {
                    throw new CborSerializationException("Value does not fit requested CBOR width ZERO");
                }
                out.write((majorType << 5) | (int) value);
            }
            case EIGHT -> {
                out.write((majorType << 5) | 24);
                out.write((int) value);
            }
            case SIXTEEN -> {
                out.write((majorType << 5) | 25);
                CborEncoder.writeShort(out, (int) value);
            }
            case THIRTY_TWO -> {
                out.write((majorType << 5) | 26);
                CborEncoder.writeInt(out, (int) value);
            }
            case SIXTY_FOUR -> {
                out.write((majorType << 5) | 27);
                CborEncoder.writeLong(out, value);
            }
            case INDEFINITE -> throw new CborSerializationException("Integers cannot use indefinite width");
        }
    }
}
