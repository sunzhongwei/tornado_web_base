tornado_web_base
================

base structure for python tornado framework

In production, you probably want to serve static files from a more optimized
static file server like nginx. You can configure most any web server to
support these caching semantics. Here is the nginx configuration we use at
FriendFeed:

location /static/ {
    root /var/friendfeed/static;
    if ($query_string) {
        expires max;
    }
 }
