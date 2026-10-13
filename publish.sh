#!/bin/bash
# Publish finp2p.info: sync this working copy to the public repo clone, commit, push, deploy.
# The public repo (github.com/alon-eth/finp2p.info) is what Vercel serves: every push to main deploys
# (GitHub app connected 2026-09-21). Pass DEPLOY=1 to also force a CLI deploy.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
CLONE="$HOME/code/finp2p.info"
MSG="${1:-update $(date +%F)}"
[ -d "$CLONE/.git" ] || git clone -q https://github.com/alon-eth/finp2p.info.git "$CLONE"
rsync -a --delete --exclude dist --exclude __pycache__ --exclude .git --exclude .vercel --exclude "data/private.json" "$SRC/" "$CLONE/"
if [ -n "$(git -C "$CLONE" status --porcelain)" ]; then
  git -C "$CLONE" add -A
  git -C "$CLONE" -c user.name="Alon Goren" -c user.email="alon@dgb.vc" commit -q -m "$MSG"
  git -C "$CLONE" pull -q --rebase origin main
  git -C "$CLONE" push -q origin main
  echo "pushed: $MSG"
else
  echo "nothing to push"
fi
if [ "${DEPLOY:-0}" = "1" ]; then (cd "$CLONE" && vercel deploy --prod --yes --scope alon-6353s-projects 2>&1 | tail -1); else echo "Vercel deploys from GitHub; watch: vercel ls finp2p-info --scope alon-6353s-projects"; fi
