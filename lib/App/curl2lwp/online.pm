package App::curl2lwp::online;
our $VERSION = '0.02';

=head1 NAME

App::curl2lwp::online - convert curl commands to Perl code online

=head1 DESCRIPTION

This is the code driving L<https://corion.net/curl2lwp.psgi>. It is a fancy web
interface to L<HTTP::Request::FromCurl> using L<Mojolicious> for the
web frontend.

It allows code generation for
L<LWP::UserAgent> and L<HTTP::Tiny>. While L<HTTP::Tiny> is smaller
and supports fewer protocols, it comes included with every modern Perl already.

This module is a placeholder to allow installation via C<cpan>.

=head1 INSTALLATION

Copy the included C<curl2lwp.cgi> command to somewhere where your webserver
can invoke it.

Alternatively, launch the program as

    curl2lwp.cgi daemon

to launch it with the Mojolicious webserver.

=cut

1;
