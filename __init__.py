# Pull all the highlighter imports up,
# so this folder can be used directly as a module
# if it's not installed the normal way.
#
# I *think* this works the way I expect?
# If not, I'll just suck it up and use __all__,
# forcing people to do `import highlighter.highlighter`,
# but that's annoying.

from highlighter import *