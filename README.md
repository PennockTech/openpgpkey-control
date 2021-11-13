openpgpkey
==========

OpenPGP Federated Keyserving support.
Take control of making your public keys available to others!

This repository has tools to help you manage making the public keys available
to others in two different ways:

1. A standalone tool you can integrate into your existing website build steps,
   eg as a Gulp task.
2. This repo is a template you can fork and use to manage the keys, either for
   a separate website or for an overlay.  Examples are included of how to go
   one step further and build a Docker image to be the webserver.


## Why

Reliability.  Safety.  Accountability.  Avoiding known current problems.

OpenPGP is a standard for some tasks in cryptography, supporting signing
things and encrypting things, without any central control authority saying who
can do what.  OpenPGP is not tied to any communications platform and there are
multiple interoperable implementations.

OpenPGP is old and has some warts; it is far from a perfect standard.  But it
is a standard and sees wide use in many problem spaces.  Tools designed for
one problem space, eg private communications, may be a better solution _there_
but folks running critical services find that OpenPGP is important for some
tasks.  It needs to work.

Historically, “public keyservers” collected lots of public keys and made them
available to all, without vetting.  It was convenient, but it was a crutch.
There are a few left, but far fewer than there used to be and the reliability
of these volunteer (or other) run services has suffered.
There are people actively trying to destroy these public-good services; the
author of the tooling here used to run such a keyserver and was active in the
community of volunteers.
_(I left because of what I perceive as a large increase in legal risk in continuing to do so.)_

There are design notes for what future public keyservers might have to do, but
the design trade-offs mean it's important for people who own PGP keys to be
able to make the full keys available under their own control.
More on that approach can be found in
<https://tools.ietf.org/html/draft-dkg-openpgp-abuse-resistant-keystore>.

So we need to make keys available, without relying upon the charity of others.
We need this to not involve a lot of manual effort by each person trying to
fetch or update a key.  Putting keys somewhere on a download site is better
than not making them available, but we need something predictable.

Each OpenPGP key has one or more user identities as part of it; usually those
contain an email address.  Email addresses use the DNS to provide federation,
and we can use that federation system, the DNS, to find places where keys in
that domain can be fetched from.

There are currently five designs for how to do this.  Three require updates to
DNS for changes in which keys are available, or even for updates to those
keys.
This has some benefits in some cases but is a non-starter for many people.
One more design is public unauthenticated LDAP, which is perhaps not something
folks will casually enter into.

This leaves one design, which lets folks with a domain setup a website to
provide keys in a fixed layout, with nothing special added to DNS beyond a
host existing.  The keys are fetched via HTTPS.  This design is called
“Web Key Directory”, WKD, which is supported by some client tooling and which
is seeing increasing adoption in the open source community, for providing the
keys of project members.

The GnuPG project have a system for updating WKD keys via email, but that's
only one approach.  If you have authoritative knowledge of which keys should
be served for which email addresses in your domain, then you can publish those
keys.

You can put these keys on the website which serves your domain apex, if you
have such a thing, or you can use the `openpgpkey` hostname inside your domain
to run a separate website.

That's where this repository comes in.
This repository is a way to track and manage the updates to keys for an
organization, and deploy them.
This is designed to be easy to fork and adapt for your use-cases, using this
as a template.
The tooling manages the life-cycle of the keys using very simple configuration
files and includes one example of how to deploy live via rsync and another
example of how to build a Docker image running a webserver for the separate
website scenario.

We also have a standalone tool for integrating into a different workflow, so
that site building flows can make including the OpenPGP keys just a single
build-step.

* <https://tools.ietf.org/html/draft-koch-openpgp-webkey-service>
* <https://wiki.gnupg.org/WKD>


## What's included here

Tools to manage the content of OpenPGP Web Key Directory websites, aka
the openpgpkey well-known area.

Optional ability to make a Docker image to act as a webserver for such a site.

You should be able to "fork" this repo to create your organization's own
canonical store, then change only the files in `config/` and use the tooling
to regenerate the rest, for your own usage.

The tools in `bin/` use configuration files in `config/` to update
`keyrings/`, `sites/` and to deploy to set content live.

All config files in `config/` allow for comment-lines starting with an
`#` octothorpe.

The `keyrings` directory is deleted and recreated by one of the tools.  
The `sites` directory is deleted and recreated by one of the tools.  
The `dns` directory (for PKA, not openpgpkey) is deleted and recreated by one
of the tools.

How the content gets served is entirely up to you, this repo does nothing to
manage remote web-server configuration.  It only manages content.

In addition, the `bundles/` directory is deleted and recreated from from
another tool; these files are not openpgpkey, but they are in the family of
"things which get published for others to rely upon".

The `other` directory contains "related tools" which might be of interest, but
are not needed for these workflows.


### Config

* `keys` lists the PGP keys to be exported; use the full fingerprint;
* `domains` lists the domains for which we should generate site content;
* `deploys` lists mappings of domains to deployment targets; a given domain
  can be deployed more than once.  The configuration and tool coding is
  written to be flexible to support more mechanisms for deployment.
* `dns-zones` lists DNS zones (domains in this context) for which we should
  generate fragments of zonefiles listing PGP-related material.
* `bundle.*` are files named for the bundle they create, listing the PGP keys
  to be included in those bundles.
* `thirdparty.*` are files listing additional keys, which will not be directly
   included in any results just because of being listed here, but signatures
   from these keys may be persisted in bundles too.


### Tools

1. `update-keyrings` requires that all keys to be exported are up-to-date in
   the current GnuPG keyring as reached with default options.
   It replaces the `keyrings/` area with fresh exports.
2. `update-sites` deletes the `sites/` area and re-creates it.
3. `update-dns-fragments` deletes the `dns/` area and re-creates it.
4. `deploy-sites` deploys the _content_ area of sites; it has no knowledge of
   administrative setup or web-server configuration.  That is outside the
   scope of this tool (or this repo, with no current plans to bring it in
   scope).
5. `update-bundles` creates keyrings from configuration files with names
   starting `bundle.`; these bundles are expected to contain cross-signatures,
   so are not made (exclusively) from the versions of the files included in
   the repo.

Each of the first three tools mutate the content of this repository, but will
often re-create the exact same content, letting Git handle the lack of
differences.  The fourth tool should make no local changes.  The fifth tool
creates content excluded from this repository.

For OpenPGP Web Key Directory content, you use the three tools, in order:
`update-keyrings`, `update-sites`, `deploy-sites`.

For DNS zonefile fragments, you use `update-keyrings` then
`update-dns-fragments`.

For bundles of distributable keyrings, you use `update-bundles`.

#### Other

* `other/standalone-update-website`: this is pretty much `deploy-sites`
  rewritten into Python with `lib/python/pdpzbase32.py` inline, so that it is
  a stdlib-only script for generating a website.
  + This tool does not use config files, it is explicitly pointed at one or
    more PGP key files to import, and it then deploys the content area.
  + This tool currently only supports the "direct method" layout, for use on a
    main web-site where OpenPGP keys are being added as additional content.
    So it does not generate a top-level stub file.
  + I wrote this adaptation to be able to use it elsewhere, but it's all based
    on this repository's code and I'm sharing it for wider use here.


### Customizing

1. Clone this repo.  "Fork" it first, if in a GitHub workflow.
2. Optionally, import our keys :-)
   + `gpg --import keyrings/*`
3. Edit files in `config/`
4. Run through the tools to update the keyrings, then the sites.
5. Commit.
6. Push to your own git remote.
7. Deploy.
   + Perhaps with the `deploy-sites` script here
   + Perhaps with something else better suited to your environment
   + Perhaps even building a container image (see below) and running that


### Docker and Caddy

These are optional, as a way to reduce setup time if you have a production
Docker/Kubernetes/whatever hosting setup.  You will need to be able to point
DNS for `openpgpkey.$YOUR_DOMAIN` at something which will map ports 80 and 443
to the running container.

The two configuration files here are _examples_ which should be customized
before use.

<a href="https://caddyserver.com/">Caddy</a> is a web-server which is
small and can automatically create and maintain HTTPS certs; this is
controlled with the `Caddyfile` configuration.  The example configuration here
is for version 2 of Caddy.

The `Caddyfile` will need to be manually updated to list the websites you wish
to serve for.

Your container image creation tools (`docker build`, `img build`, whatever)
can be driven by `Dockerfile` to create a fairly small image (22MB) to act as
a server.

The `Dockerfile` currently just installs the "standard" Caddy image, only
disabling telemetry.  For a smaller image, you can edit the Caddy main build
file to pull in fewer dependencies, or use `scratch` instead of an Alpine base
image for the final image stage.

The resulting Docker image is defined with a Volume at `/root/.caddy`: this is
used to persist the Let's Encrypt state.  **You ABSOLUTELY SHOULD persist the
Let's Encrypt state with a volume**.  Without this, every server startup will
try to get a new certificate, with a new account.

To use these for yourself, you should edit both:
 * Dockerfile: put a better maintainer label in, at least
 * Caddyfile: edit domains, and when ready switch to the staging ACME
   provider, and then to a production service
   (ie: start requesting Real certificates)

#### Example

This will run a web-server container, handling `openpgpkey.$YourDomain`, with
a persistent volume so that Caddy can maintain state.

We also remap the two exposed ports to explicit port numbers outside the
container; if you arrange for the hostname `openpgpkey.$YourDomain` to forward
ports 80 and 443 to this machine on the two mapped ports (5080 & 5443) then
you can test that this works.

```console
$ vi Dockerfile   # change maintainer, review the rest
$ vi Caddyfile    # change server hostnames
$ docker build -t openpgpkey-caddy:latest .
$ docker run -it --rm \
     -p 5080:80 -p 5443:443 \
     -v "$HOME/DockerVolumes/openpgpkey-caddy:/root/.caddy" \
     openpgpkey-caddy:latest
```

For testing on a local machine with docker, curl's `--connect-to` option will
likely help:

```sh
Site=openpgpkey.example.org
curl -k --connect-to $Site:443:localhost:5443 https://$Site/
curl -k --connect-to $Site:443:localhost:5443 https://$Site/hu/policy
gpg --with-wkd-hash --list-secret-keys
curl -sk --connect-to $Site:443:localhost:5443 https://$Site/.well-known/openpgpkey/hu/${base32str} | gpg --show-keys
```

When you've tested that everything works, comment out the staging CA usage for
the certificate and re-build the Docker image.

#### More advanced

A reasonable set of changes for a deployment is to change the service
specification to `*:8000` in the Caddyfile and remove the `tls` section;
change the Dockerfile to drop the Let's Encrypt setup and only `EXPOSE 8000`;
change the run-time user to non-root; then run the resulting image behind a
load-balancer which terminates TLS and forwards traffic across a trusted
network to the Docker container, on whichever port you expose 8000 as.

Hey presto, you can run without even container-root, and have a cloud
environment scale up and down backends as needed to meet traffic demands for
the billions of users of OpenPGP and WKD out there.


### Compliance

The content layout _should_ be compatible with
<https://datatracker.ietf.org/doc/draft-koch-openpgp-webkey-service/?include_text=1>
version `08`.

### Requirements and Constraints

#### Used Tools

* GnuPG; tested with version 2.2.19 in initial development, I expect this to
  advance.  Some tools (eg, the DNS fragments export) is known to require
  "sufficiently recent" versions of GnuPG, so something old packaged with the
  OS might not be sufficient.  I (Phil Pennock) use my packages in the apt
  repos at <https://public-packages.pennock.tech/>, installing into
  /opt/gnupg/.
* Bash
* Python (3)
* rsync, for the bundled deploy mechanism (replaceable)
* Docker / Caddy : entirely optional, for the demo container service

I am not averse to rewriting the bash scripts into Python; working code beats
adherence to local policies on maximum lengths for shell scripts.  I'm not
adverse to rewriting this all in Go, or Rust, or some other language.

But what you have here is what I'm using.  When you fork it for your own use,
feel free to swap out whatever parts you think should be replaced.  If you
feel like sharing back upstream, please consider a pull-request.


#### Design points to note

An arbitrary unfiltered key or signature upon a key from a local keyring
**MUST NEVER BE ADDED TO THE REPO**.

Dan Gillmor (dkg) has a draft for abuse-resistant keyservers,
<https://tools.ietf.org/html/draft-dkg-openpgp-abuse-resistant-keystore-03>,
which defines the term "Toxic Data".

The motivation for this repository came about in the aftermath of the collapse
of the old SKS peering mesh of HKP keyservers, which the community relied upon
for a long time.  Since spam and abuse is already happening, targeting the
keys of PGP ecosystem developers, it would be foolhardy to design a new
append-only trust store which commits in unchecked data.  Git is an
append-only trust store, in this context.  You can delete a file from the
tree, but it remains part of history without a repository rewrite and
force-pushes and garbage collection runs.

So our core specifier is the fingerprint, and we use that to update the
`keyrings/` area, which has "minimal" exports of each key: that is, the key,
its sub-keys (all self-signed by the key itself), the uids (all self-signed)
and nothing else.

For the bundles, we use "clean" exports, which allows for a signature from
another key, if that key is known to the keyring, and we arrange to ensure
that the keyring which generates those exports only includes the keys in this
repo and specified in the bundles.

If, in future, we add an "auxiliary-keys" concept, of keys which we'll track
and include the signatures of in bundles, we'll need to carefully consider
what allow in for each auxiliary key: perhaps only signatures from the
`config/aux-keys` and `config/keys` files?  Or perhaps allow for signatures
which have reciprocal signatures?  "Accept Fred's signature on Wilma's key,
but only because Fred's key has a signature by Wilma's key."


### Future

We should consider for the bundle tooling if we should keep "fatter" keyrings
in-repo: the toxic data notes in the design points above mean we'd need to
carefully define what is included in "fatter"; it could include "the same
cross-sigs which we include into the bundle"; this would at least ensure that
there are not regressions in included cross-signatures, only ever trending up.

