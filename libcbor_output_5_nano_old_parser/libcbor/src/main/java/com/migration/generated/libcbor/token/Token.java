package com.migration.generated.libcbor.token;

public sealed interface Token permits UnsignedIntToken, NegativeIntToken, ByteStringToken, TextStringToken, StartArrayToken, EndArrayToken, StartMapToken, EndMapToken, NullToken, BoolToken, FloatToken {
    // Marker interface for CBOR tokens
}
