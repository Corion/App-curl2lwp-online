#!perl
use Mojolicious::Lite;
use HTTP::Request::FromFetch;
use Filter::signatures;
use feature 'signatures';
no warnings 'experimental::signatures';
use Perl::Tidy;

my %preamble = (
    Tiny => [
        'use HTTP::Tiny;'
    ],
    LWP  => [
        'use LWP::UserAgent;'
    ],
);

sub as_perl( $ua_type, $command ) {
    $command =~ s!\\[\r\n]+! !g; # eliminate shell-style line breaks
    my @errors;
    local $SIG{__WARN__} = sub { push @errors, @_ };

    my @requests =
        eval {
            HTTP::Request::FromFetch->new(
                $command
            );
        };

    my $code = join( "\n\n",
                   @{ $preamble{ $ua_type } },
                   map { s!^    !!gm; $_ }
                   map { $_->as_snippet( type => $ua_type ) }
                   @requests
               );

    my $formatted;
    Perl::Tidy::perltidy(
        source      => \$code,
        destination => \$formatted,
        argv        => [ '--no-memoize' ],
    ) or $code = $formatted;

    return (
        version => $HTTP::Request::FromFetch::VERSION,
        command => $command,
        perl_code => $code,
        error => join( "\n", grep { defined $_ } $@, @errors, )
    );
}

get  '/' => sub( $c ) {
    $c->render(as_perl( 'LWP', 'fetch("https://example.com", { "method":"GET" })' ))
} => 'index';

post '/' => sub( $c ) {
    my( $command ) = $c->param("command");
    my( $ua_type ) = $c->param("ua_type");
    my( $parser  ) = $c->param("parser");
    my %res = as_perl( $ua_type, $command );
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
  font-family: courier, monospace;
  font-size: 1rem;
  line-height: 1.4;
  white-space: pre-wrap;
}
.codeblock {
  display: block;
  background-color: gainsboro;
  font-weight: bold;
  padding: 1rem;
  font-family: courier, monospace;
}
#error { color: red; }
.jsonly { display: hidden; }
textarea { width:100%; height:10rem; }

@@ app.js
document.addEventListener('DOMContentLoaded', function () {
  run();
});

function update() {
    $("#contact").attr('href', contactMail({
        "url":"http-request-fromcurl@corion.net",
        "subject":"About the HTTP::Request::FromCurl website",
        "body":"Hello,\nI'm writing to you about the website at "
                + window.location + ":\n"
                + "Thank you very much in advance!\n"
                + "For debugging, the context of the site is:\n\n",
        "state": ['#command', '#ua_type', '#perl_code'],
    }));
    $.ajax({
        url     : window.location.href,
        dataType: 'json',
        type    : "post",
        data    : {'command' : $('#command').val(), 'ua_type':$('#ua_type').val()},
        success : function (result) {
            $('#perl_code').text(result.perl_code);
            $("#command_comment").text( result.command );
            $('#error').text(result.error);
            $('#version').text(result.version);
        },
        error: function (error) {
            console.log("Error");
            console.log(error);
        }
    });
}

function run() {
    $(".nojs").hide();
    $(".jsonly").show();
    $("#command").on('input', update);
    $("#ua_type").on('change', update);
    $("#parser").on('change', update);

    $("#copy").click(function() { copyToClipboard($('.codeblock')) });
    $("#command").focus();
}

function copyToClipboard(element) {
    var temp = $("<textarea>");
    $("body").append(temp);
    temp.val($(element).text()).select();
    document.execCommand("copy");
    temp.remove();
}

function contactMail(options) {
    let mailBody = options["body"];
    for (var v in options["state"]) {
        let content = v + ":\n[[" + $(v).text() + "]]";
        mailBody = mailBody + "\n" + content;
    };

    let result = "mailto:"+options["url"]
               +"?subject="+encodeURI(options["subject"])
               +"&amp;body="+encodeURI(mailBody);
    return result
}

@@ index.html.ep
<!DOCTYPE html>
<html>
<head>
<title>fetch-to-lwp - Convert fetch() commands to Perl</title>
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; connect-src 'self'; style-src 'self'; script-src 'self'; worker-src 'none'; frame-src 'none'; object-src 'none'; img-src 'self'; ">
%= javascript './mojo/jquery/jquery.js'
%= javascript './app.js'
<link rel="stylesheet" href="<%= url_for 'style.css'%>" />
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@id": "curl2lwp",
  "@type": "WebApplication",
  "name": "Convert fetch() commands to Perl code",
  "url": "https://corion.net/fetch2lwp.psgi",
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
</head>
<body>
<h2>Paste your <code>fetch()</code> command here</h2>
<p><a href="curl2lwp.psgi">Switch to Curl input</a> - <a href="https://curl.se/h2c/">Headers to Curl</a></p></p>
<form method="POST" action="<%= url_for %>" enctype="application/x-www-form-urlencoded">
<textarea id="command" name="command">
<%= $command %>
</textarea>
<label for="ua_type">User-Agent module</label>
<select name="ua_type" id="ua_type">
<option value="LWP">LWP::UserAgent</option>
<option value="Tiny">HTTP::Tiny</option>
</select>
<div class="nojs">
<button type="submit">Show Perl code</button>
</div>
</form>
<h2>Resulting Perl code</h2>
<div class="jsonly">
<a href="#">Copy to clipboard</a>
</div>
<code class="codeblock">
#!perl
use strict;
use warnings;

<span id="perl_code">
<%= $perl_code %>
</span>

<%= "__END__" %>

Created from fetch() command
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
<li><a href="https://metacpan.org/pod/HTTP::Request::FromFetch">HTTP::Request::FromFetch</a> <span id="version"><%= $version %></span> for fetch() handling (<a href="https://github.com/Corion/HTTP-Request-FromCurl">Github repository</a>)</li>
% use Mojo::Util 'url_escape';
<li><a id="contact" href="mailto:http-request-fromcurl@corion.net?subject=<%= url_escape('About HTTP::Request::FromCurl'); %>&body=<%= url_escape( $command ); %>">Bug report / contact</a></li>
</ul>
</body>
</html>
