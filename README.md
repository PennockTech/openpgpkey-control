openpgpkey
==========

Tools to manage the content of OpenPGP Web Key Directory websites, aka
the openpgpkey well-known area.

Optional ability to make a Docker image to act as a webserver for such a site.

You should be able to fork this repo, change only the files in `config/` and
use the tooling to regenerate the rest, for your own usage.

The tools in `bin/` use configuration files in `config/` to update
`keyrings/`, `sites/` and to deploy to set content live.

All config files in `config/` allow for comment-lines starting with an
`#` octothorpe.

The `keyrings` directory is deleted and recreated by one of the tools.  
The `sites` directory is deleted and recreated by one of the tools.

How the content gets served is entirely up to you, this repo does nothing to
manage remote web-server configuration.  It only manages content.

In addition, the `bundles/` directory is deleted and recreated from from
another tool; these files are not openpgpkey, but they are in the family of
"things which get published for others to rely upon".


### Config

* `keys` lists the PGP keys to be exported; use the full fingerprint;
* `domains` lists the domains for which we should generate site content;
* `deploys` lists mappings of domains to deployment targets; a given domain
  can be deployed more than once.  The configuration and tool coding is
  written to be flexible to support more mechanisms for deployment.
* `bundle.*` are files named for the bundle they create, listing the PGP keys
  to be included in those bundles.


### Tools

1. `update-keyrings` requires that all keys to be exported are up-to-date in
   the current GnuPG keyring as reached with default options.
   It replaces the `keyrings/` area with fresh exports.
2. `update-sites` deletes the `sites/` area and re-creates it.
3. `deploy-sites` deploys the _content_ area of sites; it has no knowledge of
   administrative setup or web-server configuration.  That is outside the
   scope of this tool (or this repo, with no current plans to bring it in
   scope).
4. `update-bundles` creates keyrings from configuration files with names
   starting `bundle.`; these bundles are expected to contain cross-signatures,
   so are not made from the versions of the files included in the repo.

Both of the first two tools mutate the content of this repository, but will
often re-create the exact same content, letting Git handle the lack of
differences.  The third tool should make no local changes.


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
is for version 1 of Caddy, not version 2 (currently in beta).

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
 * Caddyfile: edit domains, and when ready comment out the staging ACME
   provider from Let's Encrypt to switch to the production service
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
