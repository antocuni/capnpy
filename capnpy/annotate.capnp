@0xbc24c21845631520;

# make it possible to compare/hash the structure by using the fields declared
# in the key
annotation key(struct, group) :Text;



# old way to delcare nullability, will be eventually removed
annotation nullable(group) :Void;

# tentative way to define a more flexible "nullable" annotation. Not used by
# the compiler right now

# enum Nullability {
#     ifDefault @0; # return None if the field is set to the default value
#                   # (which might !=0 if we specify a default)

#     never @1;     # never return None

#     auto @2;      # if the field has an explicit default, same as 'never';
#                   # else, same as 'ifDefault'
# }

# struct DefaultNullability {
#     int @0    :Nullability = never;
#     float @1  :Nullability = never;
#     struct @2 :Nullability = auto;
#     list @3   :Nullability = never;
#     text @4   :Nullability = never;
# }

# struct Nullable {
#     when @0 :Nullability = auto;
# }

#annotation nullable(*): Nullable; # XXX: specify a better target than '*'

enum BoolOption {
    false @0;
    true @1;
    notset @2;
}

# To add a new option:
#
#   1. add the field here
#
#   2. add it to Options.FIELDS in annotate_extended.py
#
#   3. make sure to pass a default value when you create self.default_opt in
#      compiler/module.py
#
#   4. if you add an option of type different than BoolOption, make sure that
#      Options.combine knows about it
struct Options {
    convertCase @0 :BoolOption = notset;
    canBeRoot @1 :BoolOption = notset;
}

annotation options(file, struct, field) :Options;
