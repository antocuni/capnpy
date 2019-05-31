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

struct Options {
    convertCase @0 :BoolOption = notset;
}

annotation options(file, struct, field) :Options;
