// Feature 10: Template Library
// Pre-built templates for common rental scenarios

export const templates = [
  {
    id: 'standard-apartment',
    name: 'Standard Apartment',
    description: 'Typical 1-year apartment lease with standard terms',
    icon: '&#127970;',
    data: {
      termType: 'fixed',
      unitType: 'Apartment',
      isFurnished: false,
      parkingIncluded: false,
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 8 AM',
      utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' },
      scheduleIds: ['moveInInspection', 'conditionReport'],
    },
  },
  {
    id: 'condo-rental',
    name: 'Condo Rental',
    description: 'Condo with amenities, strata/condo bylaws, parking',
    icon: '&#127959;',
    data: {
      termType: 'fixed',
      unitType: 'Condo',
      isFurnished: false,
      parkingIncluded: true,
      storageIncluded: true,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 7 AM',
      utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'included' },
      scheduleIds: ['moveInInspection', 'conditionReport', 'parking', 'storage', 'commonAreas', 'strata', 'condominium'],
    },
  },
  {
    id: 'pet-friendly',
    name: 'Pet-Friendly Rental',
    description: 'Includes pet agreement and damage expectations',
    icon: '&#128054;',
    data: {
      termType: 'fixed',
      unitType: 'Apartment',
      isFurnished: false,
      parkingIncluded: false,
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: true,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 8 AM',
      utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' },
      scheduleIds: ['moveInInspection', 'conditionReport', 'petAgreement'],
    },
  },
  {
    id: 'furnished-short',
    name: 'Furnished Short-Term',
    description: 'Fully furnished unit, all utilities included',
    icon: '&#128717;',
    data: {
      termType: 'fixed',
      unitType: 'Apartment',
      isFurnished: true,
      parkingIncluded: false,
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 8 AM',
      guestPolicy: 'Guests may stay up to 7 consecutive days',
      utilities: { heat: 'included', water: 'included', electricity: 'included', internet: 'included', cabletv: 'included', laundry: 'included', airconditioning: 'included' },
      scheduleIds: ['moveInInspection', 'conditionReport', 'keyReceipt'],
    },
  },
  {
    id: 'house-rental',
    name: 'Whole House Rental',
    description: 'House with yard/maintenance, parking, full responsibilities',
    icon: '&#127968;',
    data: {
      termType: 'fixed',
      unitType: 'House',
      isFurnished: false,
      parkingIncluded: true,
      parkingDetails: 'Driveway — 2 vehicles',
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: true,
      tenantInsuranceRequired: true,
      noisePolicy: '11 PM to 7 AM',
      utilities: { heat: 'tenant', water: 'tenant', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'tenant' },
      scheduleIds: ['moveInInspection', 'conditionReport', 'maintenance', 'petAgreement'],
      maintenanceNotes: 'Tenant responsible for lawn care (mowing, watering) and snow removal of walkways and driveway.',
    },
  },
  {
    id: 'room-shared',
    name: 'Room in Shared Dwelling',
    description: 'Single room with shared common areas',
    icon: '&#128719;',
    data: {
      termType: 'monthly',
      unitType: 'Room',
      isFurnished: true,
      parkingIncluded: false,
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: false,
      noisePolicy: '10 PM to 8 AM',
      guestPolicy: 'Guests must be approved by other occupants for stays over 3 nights',
      utilities: { heat: 'included', water: 'included', electricity: 'included', internet: 'included', cabletv: 'included', laundry: 'included', airconditioning: 'included' },
      scheduleIds: ['moveInInspection', 'commonAreas'],
    },
  },
  {
    id: 'month-to-month',
    name: 'Month-to-Month',
    description: 'Flexible periodic tenancy with no fixed end date',
    icon: '&#128197;',
    data: {
      termType: 'monthly',
      unitType: 'Apartment',
      isFurnished: false,
      parkingIncluded: false,
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 8 AM',
      utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'tenant', airconditioning: 'tenant' },
      scheduleIds: ['moveInInspection', 'conditionReport'],
    },
  },
  {
    id: 'basement-unit',
    name: 'Basement Apartment',
    description: 'Basement unit with shared laundry and separate entrance',
    icon: '&#127978;',
    data: {
      termType: 'fixed',
      unitType: 'Basement',
      isFurnished: false,
      parkingIncluded: true,
      parkingDetails: '1 driveway spot',
      storageIncluded: false,
      rentDueDay: '1st',
      paymentMethod: 'E-transfer',
      smokingAllowed: false,
      petsAllowed: false,
      tenantInsuranceRequired: true,
      noisePolicy: '10 PM to 8 AM',
      utilities: { heat: 'included', water: 'included', electricity: 'tenant', internet: 'tenant', cabletv: 'tenant', laundry: 'included', airconditioning: 'tenant' },
      scheduleIds: ['moveInInspection', 'conditionReport', 'parking'],
    },
  },
];

export function renderTemplateSelector() {
  return `
    <div class="template-grid">
      ${templates.map(t => `
        <div class="template-card" data-template="${t.id}">
          <div class="template-icon">${t.icon}</div>
          <div class="template-info">
            <strong>${t.name}</strong>
            <span>${t.description}</span>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

export function getTemplate(id) {
  return templates.find(t => t.id === id);
}
