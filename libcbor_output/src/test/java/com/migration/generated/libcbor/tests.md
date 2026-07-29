## libcbor C test mapping

- C test framework: `cmocka`
- Production Java package under test: `com.migration.generated.libcbor`

### Mapped files

- `libcbor/test/cbor_serialize_test.c` -> `CborSerializationTest.java`
  - Covers integer width encoding, byte string encoding, indefinite containers, tags, and serialized size checks.
- `libcbor/test/structurally_equal_test.c` -> `CborStructuralEqualityTest.java`
  - Covers width-sensitive structural equality, definite vs indefinite distinctions, positional array/map equality, and tag equality.
- `libcbor/test/cbor_stream_decode_test.c` and top-level façade behavior in `cbor.h` -> `CborRoundTripTest.java`
  - Covers `Cbor.serialize`, `Cbor.load`, `Cbor.loadPartial`, trailing-byte rejection, and structural equality across round-trips.
- `libcbor/test/uint_test.c` -> `CborUintTest.java`
  - Covers unsigned integer decoding from various widths, incomplete data handling, empty inputs, inline creation, and boundary conditions.
- `libcbor/test/negint_test.c` -> `CborNegintTest.java`
  - Covers negative integer decoding, width checks, magnitude calculations, and value mappings.
- `libcbor/test/unicode_test.c` -> `CborUnicodeTest.java`
  - Covers UTF-8 validation and codepoint count checks for missing bytes and invalid sequences.

### Notes

- The Java suite uses the generated production API exactly as emitted in `src/main/java`.
- Where the original C suite depends on allocator edge cases or buffer exhaustion behavior that the Java façade does not expose directly, the Java suite validates the equivalent observable behavior at the public API boundary.
