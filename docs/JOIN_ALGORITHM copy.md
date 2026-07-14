## Join Algorithm

Implement `join` in the `Relation`.

The following pseudo-code describes one way to compute the join of relations $r1$ and $r2$.

```
make the header h for the result relation
    (combine r1's header with r2's header)

make a new empty relation r using header h

for each tuple t1 in r1
    for each tuple t2 in r2

    if t1 and t2 can join
        join t1 and t2 to make tuple t
        add tuple t to relation r
    end if

    end for
end for
```

Note that the following operations used in the join should be decomposed into separate routines.

* combining r1's header with r2's header
* testing t1 and t2 to see if they can join
* joining t1 and t2

These need information about which columns between the two relations should overlap; this information should be calculated once per join operation.

Join must be able to join two relations regardless if they have common attribute names or not.

Test the new operations before using them to evaluate rules.
