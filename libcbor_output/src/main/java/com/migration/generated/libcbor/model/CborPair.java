package com.migration.generated.libcbor.model;

public record CborPair(CborItem key, CborItem value) {
    public CborPair {
        if (key == null || value == null) {
            throw new IllegalArgumentException("Map pair members must not be null");
        }
    }

    public CborPair deepCopy() {
        return new CborPair(key.deepCopy(), value.deepCopy());
    }

    public CborPair deepCopyDefinite() {
        return new CborPair(key.deepCopyDefinite(), value.deepCopyDefinite());
    }
}
