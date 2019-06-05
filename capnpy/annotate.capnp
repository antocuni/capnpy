@0xbc24c21845631520;

# make it possible to compare/hash the structure by using the fields declared
# in the key
annotation key(struct, group, field) :Text;

# render this group as a field which can be either None or a value
annotation nullable(group) :Void;

# Override the field and treat it as a group.
annotation group(field) :Text;

enum BoolOption {
    false @0;
    true @1;
    notset @2;
}

enum TextType {
    notset @0;
    bytes @1;
    unicode @2;
}

struct Options {
    versionCheck @0 :BoolOption = notset;
    convertCase @1 :BoolOption = notset;
    textType @2 :TextType = notset;
}

annotation options(file, struct, field) :Options;
