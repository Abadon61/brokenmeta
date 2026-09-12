# Guide de rédaction — légendes X & Instagram pour BrokenMeta.gg

Référence interne pour générer un fichier `.txt` de légendes à chaque fois qu'un
visuel est produit par l'outil. Format et ton calés sur les 4 premiers posts
écrits pour ce compte (`D:\Site internet\RS\00 - Text RS\`), qui appliquent déjà
correctement les mécaniques propres à chaque plateforme — ce guide documente
*pourquoi* elles sont écrites comme ça, pour rester cohérent en généralisant.

## Ce qui marche sur X (Twitter)

- **Jamais de lien dans le tweet principal.** X pénalise la portée des posts
  qui contiennent un lien sortant (l'algorithme privilégie ce qui garde les
  gens sur la plateforme). Le lien part toujours en **reply** sur son propre
  tweet, jamais dans le post qu'on veut voir circuler.
- **280 caractères, mais viser 150-200.** Un tweet plus court est presque
  toujours repris/cité plus facilement. Le chiffre-clé doit être visible dès
  la première ligne (personne ne "voit plus" sur X comme sur Instagram).
- **Une question à la fin** pour driver les réponses — les réponses comptent
  plus que les likes dans la distribution de l'algorithme X.
  - **Toujours 2 propositions** : le tweet principal + une "ALTERNATIVE"
    (angle différent, texte de remplacement, pas un post en plus) — comme un
    social media manager qui laisse le choix final à qui publie.
- **1 seul hashtag max** (`#TFT`), collé à la fin de la dernière phrase. Sur X,
  plusieurs hashtags lisent comme spam et cassent la lisibilité.
- **Sauts de ligne fréquents** : phrases courtes, une info par ligne. Un tweet
  qui ressemble à un paragraphe compact se lit moins bien dans un feed rapide.
- **Ton "vous"** (vouvoiement) — légèrement plus formel/pro que l'Instagram du
  même post, cohérent avec une audience X plus orientée actu/discussion.

## Ce qui marche sur Instagram

- **Un seul bloc, tout dans la légende** (lien compris en mention texte, pas
  cliquable — d'où "lien en bio"). Pas de reply séparé comme sur X.
- **Les ~125 premiers caractères sont ce qui s'affiche avant "plus"** : la
  ligne d'accroche doit porter le chiffre choc et se terminer par 👇 pour
  inciter à développer/scroller.
- **Corps en 2-4 paragraphes courts**, une idée par paragraphe, écrit en
  langage parlé plutôt qu'en liste sèche (sauf pour un classement, où la liste
  numérotée reste plus lisible qu'une reformulation en prose).
- **CTA "Save ce post"** avant les hashtags : sur Instagram, les
  enregistrements pèsent plus lourd que les likes dans l'algorithme de
  recommandation — donner une raison concrète de sauvegarder (comparer plus
  tard, s'en servir de référence) est plus efficace qu'un CTA générique.
- **Une question engagement** avant le CTA de save, qui invite au commentaire
  (les commentaires aussi pèsent plus que les likes).
- **Bloc hashtags à la toute fin**, 5 tags pertinents et fixes pour ce compte
  (`#TFT #TeamfightTactics #TFTMeta #Patch182 #BrokenMeta` — n'ajouter d'autres
  tags que si le contenu le justifie vraiment, ex. un nom de champion très
  recherché). Beaucoup de hashtags (10-30) n'aide plus depuis les changements
  d'algorithme récents et peut lire comme spam.
- **Alt text séparé** (champ accessibilité dédié d'Instagram, jamais collé
  dans la légende) : une phrase factuelle avec les chiffres-clés, utile à la
  fois pour l'accessibilité et le référencement interne d'Instagram.
- **Ton "tu"** (tutoiement) — plus proche/casual que le X du même post,
  cohérent avec l'audience Instagram généralement plus jeune/communautaire.

## Le fichier à générer

Un fichier par visuel, dans `D:\Site internet\RS\00 - Text RS\`, nommé
`<NN> - <type> - <sujet> - Patch X.X.txt` (numérotation qui suit celle déjà en
place dans le dossier). Structure exacte à reproduire :

```
VISUEL : <description courte du visuel>

===========================================
VERSION X (Twitter)
===========================================
⚠️ Chaque bloc ci-dessous = UN post distinct. Ne colle jamais deux blocs ensemble dans la même case.

▶▶▶ POST 1 — à publier seul (le tweet principal) — N caractères ◀◀◀
<texte>
▶▶▶ FIN DU POST 1 ◀◀◀


▶▶▶ POST 2 — à publier EN REPLY sous le Post 1 (clique "Répondre" sur ton propre tweet) — N caractères ◀◀◀
<lien brokenmeta.gg>
▶▶▶ FIN DU POST 2 ◀◀◀


▶▶▶ ALTERNATIVE — si tu préfères cet angle, REMPLACE le Post 1 par celui-ci (ne publie pas les deux) — N caractères ◀◀◀
<texte>
▶▶▶ FIN ALTERNATIVE ◀◀◀


===========================================
VERSION INSTAGRAM
===========================================
⚠️ Ce bloc-ci va TOUT en un seul endroit : la légende de la publication (colle-le en entier, hashtags compris).

<accroche 👇>

<corps, 2-4 paragraphes>

<question engagement 👇>

Retrouve <angle spécifique> sur brokenmeta.gg (lien en bio).
Save ce post <raison concrète liée au contenu>.

#TFT #TeamfightTactics #TFTMeta #Patch182 #BrokenMeta

--- Alt text (champ séparé, "texte alternatif" / "modifier le texte alternatif" sur Instagram — PAS dans la légende) ---
<phrase factuelle avec les chiffres>
```

Toujours compter les caractères réels du texte français (accents compris) pour
les annotations "— N caractères" des blocs X, et ne jamais dépasser 280.

## Process : à chaque génération de visuel

1. Générer le PNG comme d'habitude (digest → gabarit → export → `D:\Site
   internet\RS`).
2. Écrire le `.txt` de légendes correspondant avec ce gabarit, en piochant les
   chiffres exacts dans `digest.json` (jamais de chiffre inventé/arrondi
   différemment de ce qui est affiché sur le visuel).
3. Livrer les deux fichiers ensemble.
