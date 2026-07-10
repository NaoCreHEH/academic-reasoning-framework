# ScrumEval

Prototype autonome d'une plateforme d'evaluation Scrum pedagogique.

## Lancer l'application

Ouvrir `index.html` dans un navigateur.

L'application ne depend d'aucun serveur et sauvegarde les brouillons dans le stockage local du navigateur.

## Fonctionnalites incluses

- Selection d'un enseignant, d'un groupe et d'un sprint.
- Separation entre donnees communes et evaluations privees par enseignant.
- Panneau commun montrant les membres, le backlog, la story selectionnee et les validations des autres sprints.
- Validation rapide des User Stories pendant une Sprint Review.
- Titres visibles, points, coefficients, statuts et commentaires rapides par story.
- Evaluation collective par criteres.
- Evaluation quotidienne par etudiant.
- Dashboard avec score groupe, progression et classement.
- Ponderations configurables avec controle du total.
- Exports JSON, CSV, Excel CSV et synthese PDF textuelle.
- Historique des validations et changements importants.

## Donnees persistantes

Les donnees sont sauvegardees dans `localStorage` sous la cle `scrumeval-platform-v1`.
Pour repartir d'un etat vierge, supprimer cette entree dans les outils de developpement du navigateur.

## Prochaine etape technique

Pour une version multi-enseignants en temps reel, transformer ce prototype en application React/Next.js connectee a une API REST et une base PostgreSQL, avec WebSocket pour synchroniser les donnees communes.
