// Feature 8: Multi-Language Support (French for Quebec)

const translations = {
  en: {
    // Header
    'app.name': 'LeaseCreate',
    'app.tagline': 'Provincial lease agreements made simple',
    'app.privacy': 'Private — nothing leaves your browser',

    // Hero
    'hero.title.pre': 'Create a ',
    'hero.title.highlight': 'Legally Compliant',
    'hero.title.post': ' Lease',
    'hero.subtitle': 'Generate a residential tenancy agreement tailored to your province\'s legislation. Add schedules, review prohibited clauses, and export to PDF — all in your browser.',
    'hero.provinces': 'Provinces',
    'hero.schedules': 'Schedules',
    'hero.free': 'Free & Private',

    // Steps
    'step.1': 'Province & Parties',
    'step.2': 'Rental Unit',
    'step.3': 'Term & Rent',
    'step.4': 'Rules & Details',
    'step.5': 'Schedules',
    'step.6': 'Preview & Export',

    // Step 1
    'step1.title': 'Province & Parties',
    'step1.desc': 'Select your province and enter landlord/tenant information.',
    'step1.province': 'Province',
    'step1.province.placeholder': 'Select a province...',
    'step1.landlord': 'Landlord Information',
    'step1.landlord.name': 'Full Legal Name',
    'step1.landlord.email': 'Email',
    'step1.landlord.address': 'Mailing Address',
    'step1.landlord.phone': 'Phone',
    'step1.tenant': 'Tenant Information',
    'step1.tenant.name': 'Full Legal Name',
    'step1.tenant.email': 'Email',
    'step1.tenant.phone': 'Phone',
    'step1.tenant.additional': 'Additional Tenant(s)',

    // Step 2
    'step2.title': 'Rental Unit Details',
    'step2.desc': 'Describe the property being rented.',
    'step2.address': 'Street Address',
    'step2.unit': 'Unit / Suite #',
    'step2.city': 'City',
    'step2.postal': 'Postal Code',
    'step2.type': 'Unit Type',
    'step2.furnished': 'Furnished',
    'step2.parking': 'Parking included',
    'step2.storage': 'Storage locker included',

    // Step 3
    'step3.title': 'Tenancy Term & Rent',
    'step3.desc': 'Set the lease term, rent amount, and deposit details.',
    'step3.fixed': 'Fixed Term (e.g., 1 year)',
    'step3.monthly': 'Month-to-Month (Periodic)',
    'step3.start': 'Start Date',
    'step3.end': 'End Date',
    'step3.rent': 'Monthly Rent ($)',
    'step3.due': 'Due Day',
    'step3.method': 'Payment Method',
    'step3.deposits': 'Deposits',

    // Step 4
    'step4.title': 'Rules, Utilities & Details',
    'step4.desc': 'Set house rules, utility responsibilities, and additional terms.',
    'step4.smoking': 'Smoking permitted',
    'step4.pets': 'Pets permitted',
    'step4.insurance': 'Tenant insurance required',
    'step4.guest': 'Guest Policy',
    'step4.noise': 'Quiet Hours',
    'step4.utilities': 'Utilities Included in Rent',
    'step4.maintenance': 'Maintenance Notes',
    'step4.additional': 'Additional Terms',

    // Step 5
    'step5.title': 'Schedules (Additional Agreements)',
    'step5.desc': 'Select any additional schedules to attach to the lease.',

    // Step 6
    'step6.title': 'Preview & Export',
    'step6.desc': 'Review your lease agreement and export to PDF.',
    'step6.export': 'Export as PDF',
    'step6.edit': 'Edit Details',
    'step6.regenerate': 'Regenerate Preview',

    // Buttons
    'btn.next': 'Next',
    'btn.back': 'Back',
    'btn.generate': 'Generate Lease',

    // Rights sidebar
    'rights.title': 'Your Rights',
    'rights.toggle': 'Know Your Rights',

    // Drafts
    'drafts.save': 'Save Draft',
    'drafts.load': 'Load Draft',
    'drafts.delete': 'Delete',
    'drafts.saved': 'Draft saved!',
    'drafts.name': 'Draft Name',
    'drafts.empty': 'No saved drafts',

    // Templates
    'templates.title': 'Start from a Template',
    'templates.use': 'Use Template',

    // Footer
    'footer.disclaimer': 'LeaseCreate generates lease templates for informational purposes only. This is not legal advice. Consult a lawyer or your provincial tenancy board for legal guidance.',
    'footer.privacy': '100% client-side — your data never leaves your browser.',
  },
  fr: {
    'app.name': 'LeaseCreate',
    'app.tagline': 'Baux provinciaux simplifies',
    'app.privacy': 'Prive — rien ne quitte votre navigateur',

    'hero.title.pre': 'Creez un bail ',
    'hero.title.highlight': 'conforme a la loi',
    'hero.title.post': '',
    'hero.subtitle': 'Generez un bail d\'habitation adapte a la legislation de votre province. Ajoutez des annexes, verifiez les clauses interdites et exportez en PDF — le tout dans votre navigateur.',
    'hero.provinces': 'Provinces',
    'hero.schedules': 'Annexes',
    'hero.free': 'Gratuit et prive',

    'step.1': 'Province et parties',
    'step.2': 'Logement',
    'step.3': 'Duree et loyer',
    'step.4': 'Regles et details',
    'step.5': 'Annexes',
    'step.6': 'Apercu et export',

    'step1.title': 'Province et parties',
    'step1.desc': 'Selectionnez votre province et entrez les informations du locateur et du locataire.',
    'step1.province': 'Province',
    'step1.province.placeholder': 'Selectionnez une province...',
    'step1.landlord': 'Information du locateur',
    'step1.landlord.name': 'Nom legal complet',
    'step1.landlord.email': 'Courriel',
    'step1.landlord.address': 'Adresse postale',
    'step1.landlord.phone': 'Telephone',
    'step1.tenant': 'Information du locataire',
    'step1.tenant.name': 'Nom legal complet',
    'step1.tenant.email': 'Courriel',
    'step1.tenant.phone': 'Telephone',
    'step1.tenant.additional': 'Locataire(s) additionnel(s)',

    'step2.title': 'Details du logement',
    'step2.desc': 'Decrivez la propriete louee.',
    'step2.address': 'Adresse civique',
    'step2.unit': 'Unite / Appartement #',
    'step2.city': 'Ville',
    'step2.postal': 'Code postal',
    'step2.type': 'Type de logement',
    'step2.furnished': 'Meuble',
    'step2.parking': 'Stationnement inclus',
    'step2.storage': 'Casier de rangement inclus',

    'step3.title': 'Duree du bail et loyer',
    'step3.desc': 'Definissez la duree du bail, le montant du loyer et les details du depot.',
    'step3.fixed': 'Duree determinee (ex. 1 an)',
    'step3.monthly': 'Mois par mois (periodique)',
    'step3.start': 'Date de debut',
    'step3.end': 'Date de fin',
    'step3.rent': 'Loyer mensuel ($)',
    'step3.due': 'Jour d\'echeance',
    'step3.method': 'Mode de paiement',
    'step3.deposits': 'Depots',

    'step4.title': 'Regles, services et details',
    'step4.desc': 'Definissez les regles, les responsabilites des services et les conditions supplementaires.',
    'step4.smoking': 'Tabagisme permis',
    'step4.pets': 'Animaux permis',
    'step4.insurance': 'Assurance locataire requise',
    'step4.guest': 'Politique sur les invites',
    'step4.noise': 'Heures de tranquillite',
    'step4.utilities': 'Services inclus dans le loyer',
    'step4.maintenance': 'Notes d\'entretien',
    'step4.additional': 'Conditions supplementaires',

    'step5.title': 'Annexes (ententes additionnelles)',
    'step5.desc': 'Selectionnez les annexes a joindre au bail.',

    'step6.title': 'Apercu et exportation',
    'step6.desc': 'Revisez votre bail et exportez en PDF.',
    'step6.export': 'Exporter en PDF',
    'step6.edit': 'Modifier les details',
    'step6.regenerate': 'Regenerer l\'apercu',

    'btn.next': 'Suivant',
    'btn.back': 'Retour',
    'btn.generate': 'Generer le bail',

    'rights.title': 'Vos droits',
    'rights.toggle': 'Connaissez vos droits',

    'drafts.save': 'Sauvegarder le brouillon',
    'drafts.load': 'Charger un brouillon',
    'drafts.delete': 'Supprimer',
    'drafts.saved': 'Brouillon sauvegarde!',
    'drafts.name': 'Nom du brouillon',
    'drafts.empty': 'Aucun brouillon sauvegarde',

    'templates.title': 'Commencer a partir d\'un modele',
    'templates.use': 'Utiliser ce modele',

    'footer.disclaimer': 'LeaseCreate genere des modeles de bail a titre informatif seulement. Ceci ne constitue pas un avis juridique. Consultez un avocat ou votre regie du logement.',
    'footer.privacy': '100% cote client — vos donnees ne quittent jamais votre navigateur.',
  },
};

let currentLang = 'en';

export function setLanguage(lang) {
  currentLang = lang;
  applyTranslations();
}

export function getLanguage() {
  return currentLang;
}

export function t(key) {
  return translations[currentLang]?.[key] || translations.en[key] || key;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const text = t(key);
    if (!text) return;
    // Only set text on leaf nodes (no children that also have data-i18n or are interactive)
    // Use innerText only if element has no child elements we need to preserve
    if (el.children.length === 0) {
      el.textContent = text;
    } else {
      // Find the first text node and update it, preserving child elements
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, null);
      const firstText = walker.nextNode();
      if (firstText) firstText.textContent = text;
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    const text = t(key);
    if (text) el.placeholder = text;
  });

  document.documentElement.lang = currentLang;
}
