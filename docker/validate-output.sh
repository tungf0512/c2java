#!/usr/bin/env bash
# Independently validate the generated Java project.
#
# Does not trust the pipeline's "Migration completed" message: rebuilds from
# clean and runs the assertions from the original C test against the Java.
set -uo pipefail

REPO="/root/rustprint-output/${C_PROJECT_NAME}"

echo "=== 1. Structure ==="
for required in pom.xml src/main/java; do
  if [ -e "$REPO/$required" ]; then echo "  OK      $required"; else echo "  MISSING $required"; exit 1; fi
done
echo "  java files: $(find "$REPO/src" -name '*.java' | wc -l)"

echo
echo "=== 2. Clean Maven compile ==="
rm -rf "$REPO/target"
if mvn -q -f "$REPO/pom.xml" clean compile; then
  echo "  BUILD OK (from clean, no stale target/)"
else
  echo "  BUILD FAILED"; exit 1
fi

echo
echo "=== 3. Behaviour vs the original C test ==="
# dummy_c_project/tests/test_geometry.c asserts (1,2)+(3,4) == (4,6).
cat > /tmp/CheckGeometry.java <<'JAVA'
import com.migration.generated.dummy_c_project.geometry.Geometry;
import com.migration.generated.dummy_c_project.geometry.Point;

public class CheckGeometry {
    public static void main(String[] args) {
        Point p1 = new Point(1, 2);
        Point p2 = new Point(3, 4);
        Point sum = Geometry.addPoints(p1, p2);

        if (sum.x() != 4) throw new AssertionError("expected x=4, got " + sum.x());
        if (sum.y() != 6) throw new AssertionError("expected y=6, got " + sum.y());

        Point neg = Geometry.addPoints(new Point(-5, 7), new Point(5, -7));
        if (neg.x() != 0 || neg.y() != 0) throw new AssertionError("negative case failed: " + neg);

        System.out.println("  (1,2)+(3,4) = (" + sum.x() + "," + sum.y() + ")  matches the C assertion");
        System.out.println("  (-5,7)+(5,-7) = (" + neg.x() + "," + neg.y() + ")");
        System.out.println("  BEHAVIOUR OK");
    }
}
JAVA

if java -cp "$REPO/target/classes" /tmp/CheckGeometry.java; then
  echo
  echo "=== VERDICT: the generated project compiles and is behaviourally correct ==="
else
  echo "  BEHAVIOUR FAILED"; exit 1
fi
