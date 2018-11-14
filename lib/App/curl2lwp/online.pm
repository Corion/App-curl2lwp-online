package App::curl2lwp::online;
our $VERSION = '0.01';

=head1 NAME

App::curl2lwp::online - convert curl commands to LWP::UserAgent Perl code online

=head1 DESCRIPTION

This is the code driving L<https://corion.net/curl2lwp.psgi>. It is a fancy web
interface to L<HTTP::Request::FromCurl> using L<Mojolicious> for the
web frontend.

This module is a placeholder to allow installation via C<cpan>.

=head1 INSTALLATION

Copy the included C<curl2lwp.cgi> command to somewhere where your webserver
can invoke it.

Alternatively, launch the program as

    curl2lwp.cgi daemon

to launch it with the Mojolicious webserver.

=cut

1;