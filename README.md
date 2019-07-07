openpgpkey
==========

Tools to manage the content of openpgpkey websites.

The tools in `bin/` use configuration files in `config/` to update
`keyrings/`, `sites/` and to deploy to set content live.

All config files in `config/` allow for comment-lines starting with an
`#` octothorpe.

The `sites` directory is deleted and recreated by one of the tools.

### Config

* `keys` lists the PGP keys to be exported; use the full fingerprint;
* `domains` lists the domains for which we should generate site content;
* `deploys` lists mappings of domains to deployment targets; a given domain
  can be deployed more than once.  The configuration and tool coding is
  written to be flexible to support more mechanisms for deployment.

### Tools

1. `update-keyrings` requires that all keys to be exported are up-to-date in
   the current GnuPG keyring as reached with default options.  It updates
   files in `keyrings/` with dumps.
2. `update-sites` deletes the `sites/` area and re-creates it.
3. `deploy-sites` deploys the _content_ area of sites; it has no knowledge of
   administrative setup or web-server configuration.  That is outside the
   scope of this tool (or this repo, with no current plans to bring it in
   scope).

### Compliance

The content layout _should_ be compatible with
<https://datatracker.ietf.org/doc/draft-koch-openpgp-webkey-service/?include_text=1>
version `08`.
