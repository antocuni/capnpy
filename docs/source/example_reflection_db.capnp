@0x801e5c7f340eaf8f;

annotation dbTable(struct) :Text;
annotation dbPrimaryKey(field) :Void;

struct Person $dbTable("Persons") {
    id @0 :UInt64 $dbPrimaryKey;
    firstName @1 :Text;
    lastName @2 :Text;
    school @3 :UInt64;
}

struct School $dbTable("Schools") {
    id @0 :UInt64 $dbPrimaryKey;
    name @1 :Text;
    city @2 :Text;
}
