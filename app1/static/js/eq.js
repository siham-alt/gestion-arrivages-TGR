document.addEventListener('DOMContentLoaded', () => {
    // Éléments du DOM
    const categoriesList = document.getElementById('categories-list');
    const equationZone = document.getElementById('equation-zone');
    const equationDisplay = document.getElementById('equation-display');
    const constantInput = document.getElementById('constant-input');
    const sumCoefficientsSpan = document.getElementById('sum-coefficients');
    const validationMessage = document.getElementById('validation-message');
    const saveButton = document.getElementById('save-equation-btn');

    // Données des matières premières (simulées pour l'instant)
    // En production, ces données viendraient d'une API (fetch('/api/matieres/'))
    let allMatiereData = [
        { id: 1, categorie: "Métaux Précieux", code: "OR", libelle: "Or" },
        { id: 2, categorie: "Métaux Précieux", code: "AG", libelle: "Argent" },
        { id: 3, categorie: "Métaux Industriels", code: "AL", libelle: "Aluminium" },
        { id: 4, categorie: "Métaux Industriels", code: "CU", libelle: "Cuivre" },
        { id: 5, categorie: "Métaux Industriels", code: "ZN", libelle: "Zinc" },
        { id: 6, categorie: "Énergies", code: "BRUT", libelle: "Pétrole Brut" },
        { id: 7, categorie: "Énergies", code: "GAZ", libelle: "Gaz Naturel" },
        { id: 8, categorie: "Agriculture", code: "BLÉ", libelle: "Blé" },
        { id: 9, categorie: "Agriculture", code: "MAIS", libelle: "Maïs" },
        { id: 10, categorie: "Chimie", code: "SOD", libelle: "Sodium" },
        { id: 11, categorie: "Chimie", code: "SUL", libelle: "Acide Sulfurique" }
    ];


    // État actuel de l'équation construite
    let equationTerms = []; // Ex: [{ id: 3, code: "AL", libelle: "Aluminium", coefficient: 0.2 }]
    let equationConstant = parseFloat(constantInput.value) || 0;

    // --- Fonctions de Rendu et Logique ---

    // 1. Rendre la liste des matières premières disponibles
    function renderMatiereList() {
        categoriesList.innerHTML = ''; // Nettoyer le contenu existant
        if (allMatiereData.length === 0) {
            categoriesList.innerHTML = '<p>Aucune matière première disponible.</p>';
            return;
        }

        // Pour l'instant, on affiche tout en une seule liste.
        // Plus tard, on pourra regrouper par catégorie si nécessaire.
        allMatiereData.forEach(matiere => {
            const matiereDiv = document.createElement('div');
            matiereDiv.classList.add('matiere-item');
            matiereDiv.draggable = true; // Rendre l'élément draggable
            matiereDiv.textContent = `${matiere.code} (${matiere.libelle})`;
            
            // Stocker les données de la matière dans l'attribut data-* et pour le dragstart
            matiereDiv.dataset.id = matiere.id;
            matiereDiv.dataset.code = matiere.code;
            matiereDiv.dataset.libelle = matiere.libelle;

            // Événement dragstart: enregistrer les données de l'élément glissé
            matiereDiv.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('application/json', JSON.stringify({
                    id: matiere.id,
                    code: matiere.code,
                    libelle: matiere.libelle
                }));
                // Optionnel: ajouter une classe pour un feedback visuel pendant le drag
                matiereDiv.classList.add('dragging');
            });

            // Événement dragend: nettoyer après le drag
            matiereDiv.addEventListener('dragend', (e) => {
                matiereDiv.classList.remove('dragging');
            });

            categoriesList.appendChild(matiereDiv);
        });
    }

    // 2. Gérer le glisser-déposer sur la zone de l'équation
    equationZone.addEventListener('dragover', (e) => {
        e.preventDefault(); // Empêche le comportement par défaut (interdit le drop)
        equationZone.classList.add('drag-over'); // Ajoute une classe pour un feedback visuel
    });

    equationZone.addEventListener('dragleave', () => {
        equationZone.classList.remove('drag-over'); // Retire la classe quand on quitte la zone
    });

    equationZone.addEventListener('drop', (e) => {
        e.preventDefault();
        equationZone.classList.remove('drag-over'); // Retire la classe après le drop

        const data = e.dataTransfer.getData('application/json');
        if (data) {
            const matiereData = JSON.parse(data);
            addTermToEquation(matiereData);
        }
    });

    // 3. Ajouter un terme à l'équation
    function addTermToEquation(matiereData) {
        // Vérifier si la matière est déjà dans l'équation
        if (equationTerms.some(term => term.id === matiereData.id)) {
            alert(`"${matiereData.libelle}" est déjà présente dans l'équation.`);
            return;
        }

        // Retirer le texte d'instruction si c'est le premier terme
        const placeholder = equationZone.querySelector('.placeholder-text');
        if (placeholder) {
            placeholder.remove();
        }

        const newTerm = {
            id: matiereData.id,
            code: matiereData.code,
            libelle: matiereData.libelle,
            coefficient: 0 // Coefficient initial par défaut
        };
        equationTerms.push(newTerm);
        renderEquationTerms(); // Re-rendre tous les termes
        updateEquationDisplay(); // Mettre à jour l'affichage de l'équation
        validateCoefficients(); // Valider les coefficients après ajout
    }

    // 4. Rendre les termes de l'équation dans la zone
    function renderEquationTerms() {
        equationZone.innerHTML = ''; // Nettoyer tous les termes existants

        if (equationTerms.length === 0) {
            const placeholder = document.createElement('p');
            placeholder.classList.add('placeholder-text');
            placeholder.textContent = 'Faites glisser les matières premières ici pour construire votre équation.';
            equationZone.appendChild(placeholder);
        } else {
            equationTerms.forEach((term) => {
                const termDiv = document.createElement('div');
                termDiv.classList.add('equation-term');
                termDiv.innerHTML = `
                    <input type="number" step="0.01" min="0" max="1" class="coefficient-input" value="${term.coefficient}">
                    <span>${term.code} (${term.libelle})</span>
                    <button class="remove-term" data-id="${term.id}">X</button>
                `;

                // Écouter les changements de coefficient
                const coeffInput = termDiv.querySelector('.coefficient-input');
                coeffInput.addEventListener('input', (e) => {
                    term.coefficient = parseFloat(e.target.value) || 0;
                    validateCoefficients();
                    updateEquationDisplay();
                });

                // Écouter le clic sur le bouton de suppression
                const removeButton = termDiv.querySelector('.remove-term');
                removeButton.addEventListener('click', () => {
                    removeTermFromEquation(term.id);
                });

                equationZone.appendChild(termDiv);
            });
        }
    }

    // 5. Supprimer un terme de l'équation
    function removeTermFromEquation(id) {
        equationTerms = equationTerms.filter(term => term.id !== id);
        renderEquationTerms(); // Re-rendre les termes
        validateCoefficients(); // Re-valider
        updateEquationDisplay(); // Mettre à jour l'affichage
    }

    // 6. Valider la somme des coefficients
    function validateCoefficients() {
        const sum = equationTerms.reduce((acc, term) => acc + term.coefficient, 0);
        sumCoefficientsSpan.textContent = sum.toFixed(2); // Afficher la somme

        const isValid = Math.abs(sum - 1) < 0.001; // Tolérance pour les nombres flottants

        if (isValid) {
            validationMessage.textContent = "Somme des coefficients = 1.00 (Valide)";
            validationMessage.className = 'validation-message success';
            saveButton.disabled = false; // Activer le bouton d'enregistrement
        } else {
            validationMessage.textContent = `Somme des coefficients = ${sum.toFixed(2)}. Doit être égale à 1.00.`;
            validationMessage.className = 'validation-message error';
            saveButton.disabled = true; // Désactiver le bouton d'enregistrement
        }
    }

    // 7. Mettre à jour l'affichage textuel de l'équation
    function updateEquationDisplay() {
        let equationString = "y = ";
        const activeTerms = equationTerms.filter(term => term.coefficient !== 0);

        if (activeTerms.length === 0 && equationConstant === 0) {
            equationString += "0";
        } else {
            activeTerms.forEach((term, index) => {
                equationString += `${term.coefficient.toFixed(2)} ${term.code}`;
                if (index < activeTerms.length - 1) {
                    equationString += " + ";
                }
            });
            if (equationConstant !== 0) {
                if (activeTerms.length > 0) {
                    equationString += " + ";
                }
                equationString += `${equationConstant.toFixed(2)}`;
            }
        }
        equationDisplay.textContent = equationString;
    }

    // 8. Gérer le changement de la constante 'c'
    constantInput.addEventListener('input', (e) => {
        equationConstant = parseFloat(e.target.value) || 0;
        updateEquationDisplay();
    });

    // 9. Gérer l'enregistrement de l'équation (simulé pour l'instant)
    saveButton.addEventListener('click', () => {
        if (!saveButton.disabled) {
            const finalEquation = {
                termes: equationTerms.map(term => ({
                    id: term.id,
                    code: term.code,
                    coefficient: term.coefficient
                })),
                constante: equationConstant
            };
            console.log("Équation à sauvegarder (JSON) :", JSON.stringify(finalEquation, null, 2));
            alert("Équation prête à être sauvegardée ! Voir la console pour le JSON.");
            // Ici, vous enverriez `finalEquation` à votre API backend via fetch() POST
        }
    });

    // --- Initialisation au chargement de la page ---
    renderMatiereList(); // Affiche les matières disponibles
    renderEquationTerms(); // Initialise la zone d'équation (avec le placeholder)
    validateCoefficients(); // Vérifie la validation initiale
    updateEquationDisplay(); // Met à jour l'affichage initial de l'équation
});