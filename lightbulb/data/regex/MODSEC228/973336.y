s [ ]
w [a-z0-9A-Z]
W [^a-z0-9A-Z]
d [0-9]
%%
((i)(\<script[^\>]*\>[ \S]*\<\/script[^\>]*\>|\<script[^\>]*\>[ \S]*\<\/script[[ \S]]*[ \S]|\<script[^\>]*\>[ \S]*\<\/script[ ]*[ ]|\<script[^\>]*\>[ \S]*\<\/script|\<script[^\>]*\>[ \S]*)) printf('attack detected');
%%
