#!/bin/bash
# Publish finp2p.info: sync this working copy to the public repo clone, commit, push, deploy.
# The public repo (github.com/alon-eth/finp2p.info) is what Vercel serves. Until the Vercel GitHub
# app is installed for alon-eth, the deploy step here is what ships; after that, the push alone does.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
CLONE="$HOME/code/finp2p.info"
MSG="${1:-update $(date +%F)}"
[ -d "$CLONE/.git" ] || git clone -q https://github.com/alon-eth/finp2p.info.git "$CLONE"
rsync -a --delete --exclude dist --exclude __pycache__ --exclude .git --exclude .vercel "$SRC/" "$CLONE/"
if [ -n "$(git -C "$CLONE" status --porcelain)" ]; then
  git -C "$CLONE" add -A
  git -C "$CLONE" -c user.name="Alon Goren" -c user.email="alon@dgb.vc" commit -q -m "$MSG"
  git -C "$CLONE" pull -q --rebase origin main
  git -C "$CLONE" push -q origin main
  echo "pushed: $MSG"
else
  echo "nothing to push"
fi
(cd "$CLONE" && vercel deploy --prod --yes --scope alon-6353s-projects 2>&1 | tail -1)
