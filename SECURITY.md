# Security Policy

## Supported versions

Only the latest release of Qascade receives security fixes.

## Reporting a vulnerability

Please do not open a public issue for a security problem. Report it privately in one of these ways:

- Use GitHub's private vulnerability reporting: open the
  [Security tab](https://github.com/Suman-Poola/Qascade/security/advisories/new) of the repository
  and choose "Report a vulnerability".
- Or email the maintainer at spoola@imsa.edu.

Include the affected version, a description of the problem, and steps to reproduce it. You can
expect an acknowledgement within a few days. Qascade is maintained by one person, so fixes are
made on a best-effort basis.

## Saved model files

Model files written by `qascade.save_model` contain pickled data. Unpickling can run arbitrary code,
so only load model files from sources you trust, and never load one received from an unknown
party.
