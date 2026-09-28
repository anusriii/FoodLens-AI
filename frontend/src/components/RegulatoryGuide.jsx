import React from 'react';

export default function RegulatoryGuide() {
  const authorities = [
    {
      country: 'India',
      flag: '🇮🇳',
      agency: 'FSSAI (Food Safety and Standards Authority of India)',
      framework: 'Food Safety and Standards Act, 2006 & Regulations, 2011',
      highlights: [
        'Mandatory green/brown veg/non-veg dot identification',
        'Specific INS codes required for food additives and synthetic colours',
        'Nutritional declaration per 100g or per serving with added sugar and saturated fat disclosure',
        'Strict limits on synthetic food colours (max 100 ppm in most snacks and confectionery)',
      ],
      url: 'https://www.fssai.gov.in/',
    },
    {
      country: 'USA',
      flag: '🇺🇸',
      agency: 'US FDA (Food and Drug Administration)',
      framework: 'Federal Food, Drug, and Cosmetic Act & 21 CFR (Code of Federal Regulations)',
      highlights: [
        'FALCPA & FASTER Act: 9 major priority food allergens (Milk, Eggs, Fish, Crustaceans, Tree Nuts, Peanuts, Wheat, Soy, Sesame)',
        'GRAS (Generally Recognized as Safe) additive regulatory classification',
        'Mandatory Dual-Column Nutrition Facts label for multi-serving containers',
        'Specific naming requirements for certified color additives (e.g. FD&C Yellow No. 5)',
      ],
      url: 'https://www.fda.gov/food',
    },
    {
      country: 'European Union',
      flag: '🇪🇺',
      agency: 'European Commission & EFSA (European Food Safety Authority)',
      framework: 'Regulation (EC) No 1333/2008 & Regulation (EU) No 1169/2011 (FIC)',
      highlights: [
        'Mandatory E-number or official chemical name declaration with technological functional category',
        'Mandatory warning label for Southampton azo dyes: "May have an adverse effect on activity and attention in children"',
        '14 priority allergens required to be highlighted (bold, underlined) in ingredient list',
        'Standardized mandatory nutrition declaration on per 100g or per 100ml basis',
      ],
      url: 'https://food.ec.europa.eu/safety_en',
    },
    {
      country: 'UK',
      flag: '🇬🇧',
      agency: 'UK Food Standards Agency (FSA) & Food Standards Scotland',
      framework: 'Food Safety Act 1990 & Retained EU Regulation 1169/2011 & Natasha\'s Law',
      highlights: [
        'Natasha\'s Law: Full ingredient and allergen labelling required on Prepacked for Direct Sale (PPDS) foods',
        'UK Register of Regulated Food Additives post-Brexit',
        'Front-of-pack traffic light nutritional voluntary scheme (Red/Amber/Green)',
      ],
      url: 'https://www.food.gov.uk/',
    },
    {
      country: 'Canada',
      flag: '🇨🇦',
      agency: 'Health Canada & Canadian Food Inspection Agency (CFIA)',
      framework: 'Food and Drugs Act (FDA) & Food and Drug Regulations (FDR)',
      highlights: [
        'Positive Lists of Permitted Food Additives published and maintained by Health Canada',
        'Bilingual labelling requirements (English and French) for consumer packages',
        'Front-of-package (FOP) high saturated fat, sugar, and sodium nutrition warning symbol regulations',
        'Specific allergen, gluten source, and added sulphite declarations',
      ],
      url: 'https://www.canada.ca/en/health-canada/services/food-nutrition.html',
    },
  ];

  return (
    <div className="card reg-guide-card">
      <div className="card-header">
        <div>
          <h2 className="card-title">Official Global Food Regulatory Standards</h2>
          <span className="card-subtitle">
            Authoritative reference criteria used by FoodLens AI's deterministic rule engine
          </span>
        </div>
        <span className="badge badge-accent">Statutory Reference</span>
      </div>

      <div className="card-body">
        <div className="authorities-grid">
          {authorities.map((auth, idx) => (
            <div key={idx} className="authority-card">
              <div className="auth-header">
                <span className="auth-flag">{auth.flag}</span>
                <div>
                  <h3 className="auth-country">{auth.country}</h3>
                  <span className="auth-agency">{auth.agency}</span>
                </div>
              </div>

              <div className="auth-body">
                <p className="auth-framework">
                  <strong>Statutory Framework:</strong> {auth.framework}
                </p>
                <div className="auth-highlights">
                  <strong>Key Regulatory Principles:</strong>
                  <ul>
                    {auth.highlights.map((h, hIdx) => (
                      <li key={hIdx}>{h}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="auth-footer">
                <a
                  href={auth.url}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-link"
                >
                  Visit Official Agency Portal ↗
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
