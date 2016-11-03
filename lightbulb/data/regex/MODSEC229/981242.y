s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((([\"\'\`]{s}*(x?or|div|like|between|and){s}*[\"\'\`]?{d})|(\\\\x(23|27|3d))|(^.?[\"\'\`]$)|((^[\"\'\`\\\\]*([0-9\"\'\`]+|[^\"\'\`]+[\"\'\`]))+{s}*(n?and|x?x?or|div|like|between|and|not|\|\||\&\&){s}*[a-zA-Z\"\'\`][+\&\!\@\\(\\),.\-])|([^a-zA-Z ]{w}+{s}*[|\-]{s}*[\"\'\`]{s}*{w})|(\@{w}+{s}+(and|x?or|div|like|between|and){s}*[0-9\"\'\`]+)|(\@[a-zA-Z\-]+{s}(and|x?or|div|like|between|and){s}*[^a-zA-Z ])|([^a-zA-Z \:]{s}*{d}{W}+[^a-zA-Z ]{s}*[\"\'\`].)|({W}information\_schema|table\_name{W}))) printf('attack detected');
%%
