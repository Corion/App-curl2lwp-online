#!perl
use Mojolicious::Lite;
use HTTP::Request::FromCurl;
use Filter::signatures;
use feature 'signatures';
no warnings 'experimental::signatures';
use Perl::Tidy;

sub as_lwp( $command ) {
    $command =~ s!\\[\r\n]+! !g; # eliminate shell-style line breaks
    my @errors;
    local $SIG{__WARN__} = sub { push @errors, @_ };

    my @requests =
        eval {
            HTTP::Request::FromCurl->new(
                command_curl => $command,
                read_files => 0,
            );
        };

    my $code = join( "\n\n",
                   map { s!^    !!gm; $_ }
                   map { $_->as_snippet }
                   @requests
               );
    my $formatted;
    Perl::Tidy::perltidy(
        source      => \$code,
        destination => \$formatted,
        argv        => [ '--no-memoize' ],
    ) or $code = $formatted;

    return (
        version => $HTTP::Request::FromCurl::VERSION,
        command => $command,
        perl_code => $code,
        error => join( "\n", grep { defined $_ } $@, @errors, )
    );
}

get  '/' => sub( $c ) {
    $c->render(as_lwp( 'curl -X GET -A pcurl/1.0 https://example.com --data-binary @/etc/passwd' ))
} => 'index';

post '/' => sub( $c ) {
    my( $command ) = $c->param("command");
    my %res = as_lwp( $command );
    $c->respond_to(
        json => { json => \%res },
        html => sub { $c->render( %res ); },
    )
} => 'index';

app->start;

__DATA__

@@ style.css
html {
  font-size: medium;
}

body {
  background-color: #fffff6;
  color: #330;
  font-family: georgia, times, serif;
  margin: 2rem auto;
  max-width: 48em;
  padding: 0 2em;
  width: auto;
  font-size: 1rem;
  line-height: 1.4;
}

a {
  color: #1e6b8c;
  font-size: 1em;
  text-decoration: none;
  transition-delay: 0.1s;
  transition-duration: 0.3s;
  transition-property: color, background-color;
  transition-timing-function: linear;
}

a:visited {
  color: #6f32ad;
  font-size: 1em;
}

a:hover {
  background: #f0f0ff;
  font-size: 1em;
  text-decoration: underline;
}

a:active {
  background-color: #427fed;
  color: #fffff6;
  color: white;
  font-size: 1em;
}

h1,
h2,
h3,
h4,
h5,
h6 {
  color: #703820;
  font-weight: bold;
  line-height: 1.2;
  margin-bottom: 1em;
  margin-top: 2em;
}

h1 {
  font-size: 2.2em;
  text-align: center;
}

h2 {
  font-size: 1.8em;
  border-bottom: solid 0.1rem #703820;
}

h3 {
  font-size: 1.5em;
}

h4 {
  font-size: 1.3em;
  text-decoration: underline;
}

h5 {
  font-size: 1.2em;
  font-style: italic;
}

h6 {
  font-size: 1.1em;
  margin-bottom: 0.5rem;
}

pre,
code,
xmp {
  font-family: courier;
  font-size: 1rem;
  line-height: 1.4;
  white-space: pre-wrap;
}
.codeblock {
  display: block;
  background-color: gainsboro;
  font-weight: bold;
  padding: 1rem;
}
#error { color: red; }
.jsonly { display: hidden; }

@@ index.html.ep
<!DOCTYPE html>
<html>
<head>
<title>Curl-to-lwp - Convert Curl command lines to Perl</title>
%= javascript '/mojo/jquery/jquery.js'
<link rel="stylesheet" href="<%= url_for 'style.css'%>" />
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@id": "curl2lwp",
  "@type": "WebApplication",
  "name": "Convert Curl command to Perl code",
  "url": "https://corion.net/curl2lwp.psgi",
  "applicationCategory": "Utility",
  "applicationSubCategory": "Programming",
  "about": "This converts Curl commands to Perl code",
  "browserRequirements": "",
  "softwareVersion": "<%= $version %>",
  "screenshot": "[image-url]",
  "inLanguage":[{
      "@type": "Language",
      "name": "English",
      "alternateName": "en",
      "additionalType":"https://www.loc.gov/standards/iso639-2/php/code_list.php",
      "sameAs":"https://en.wikipedia.org/wiki/English_language"
    }
],
  "softwareHelp": {
    "@type": "CreativeWork",
      "name":"Customer Service and Support",
      "url": [
      "https://example.com/en/help.html"
      ]
  },
  "operatingSystem": "All"
}
</script>

<script>
function run() {
    $(".nojs").hide();
    $(".jsonly").show();
    $("#command").on('input', function(){
        $.ajax({
            url     : "<% url_for %>",
            dataType: 'json',
            type    : "post",
            data    : {'command' : $(this).val()},
            success : function (result) {
                $('#perl_code').text(result.perl_code);
                $("#command_comment").text( result.command );
                $('#error').text(result.error);
                $('#version').text(result.version);
            },
            error: function (error) {
                console.log("Error");
                console.log(result);
            }
        });

    });
    $("#command").focus();
}
$(document).ready(run);

function copyToClipboard(element) {
    var temp = $("<textarea>");
    $("body").append(temp);
    temp.val($(element).text()).select();
    document.execCommand("copy");
    temp.remove();
}

</script>
</head>
<body>
<h2>Paste your Curl command here</h2>
<form method="POST" action="<%= url_for %>">
<textarea id="command" name="command" style="width:100%; height:10rem">
<%= $command %>
</textarea>
<div class="nojs">
<button type="submit">Show Perl code</button>
</div>
</form>
<h2>Resulting Perl code</h2>
<div class="jsonly">
<a href="#" onclick="javascript:copyToClipboard($('.codeblock'))">Copy to clipboard</a>
</div>
<code class="codeblock">
#!perl
use strict;
use warnings;
use WWW::Mechanize;
use HTTP::Request;

<span id="perl_code">
<%= $perl_code %>
</span>

<%= "__END__" %>

Created from curl command line
<span id="command_comment">
<%= $command %>
</span>
</code>
<div id="error">
<%= $error %>
</div>
<h2>Powered by</h2>
<ul>
<li><a href="https://mojolicious.org">Mojolicious</a> for highly convenient web stuff</li>
<li><a href="https://metacpan.org/pod/HTTP::Request::FromCurl">HTTP::Request::FromCurl</a> <span id="version"><%= $version %></span> for Curl handling (<a href="https://github.com/Corion/HTTP-Request-FromCurl">Github repository</a>)</li>
<li><a href="mailto:http-request-fromcurl@corion.net">Bug report / contact</a></li>
</ul>
<h></p>
</body>
</html>