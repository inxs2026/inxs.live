// Feature 7: Lease Timeline
// Visual timeline of key dates and deadlines

export function generateTimeline(formData, province) {
  if (!formData.startDate) return '';

  const start = new Date(formData.startDate + 'T00:00:00');
  const events = [];

  // Move-in date
  events.push({
    date: start,
    label: 'Move-In Date',
    type: 'primary',
    desc: 'Tenancy begins',
  });

  // First rent due
  const firstRent = new Date(start);
  if (formData.rentDueDay === '1st') {
    firstRent.setMonth(firstRent.getMonth() + (firstRent.getDate() === 1 ? 0 : 1));
    firstRent.setDate(1);
  } else if (formData.rentDueDay === '15th') {
    if (firstRent.getDate() > 15) firstRent.setMonth(firstRent.getMonth() + 1);
    firstRent.setDate(15);
  }
  events.push({
    date: firstRent,
    label: 'First Rent Payment',
    type: 'info',
    desc: `$${formData.rentAmount} due`,
  });

  // End date (fixed term)
  if (formData.termType === 'fixed' && formData.endDate) {
    const end = new Date(formData.endDate + 'T00:00:00');
    events.push({
      date: end,
      label: 'Lease End Date',
      type: 'danger',
      desc: 'Fixed term expires',
    });

    // Tenant notice deadline
    const noticeDeadline = new Date(end);
    if (['ON', 'MB'].includes(province.code)) {
      noticeDeadline.setDate(noticeDeadline.getDate() - 60);
      events.push({
        date: noticeDeadline,
        label: 'Tenant Notice Deadline',
        type: 'warning',
        desc: '60 days before end — last day to give notice of termination',
      });
    } else if (province.code === 'BC') {
      noticeDeadline.setMonth(noticeDeadline.getMonth() - 1);
      events.push({
        date: noticeDeadline,
        label: 'Tenant Notice Deadline',
        type: 'warning',
        desc: '1 month before end — last day to give notice',
      });
    } else if (province.code === 'QC') {
      const months = getMonthsDiff(start, end);
      const noticeDays = months >= 12 ? 180 : 90;
      noticeDeadline.setDate(noticeDeadline.getDate() - noticeDays);
      events.push({
        date: noticeDeadline,
        label: 'Notice Deadline (QC)',
        type: 'warning',
        desc: `${noticeDays / 30} months before end — last day to give modification/termination notice`,
      });
    }

    // Rent increase eligibility (12 months from start)
    if (province.rentRules.rentIncreaseGuideline) {
      const increaseDate = new Date(start);
      increaseDate.setFullYear(increaseDate.getFullYear() + 1);
      if (increaseDate <= end) {
        events.push({
          date: increaseDate,
          label: 'Earliest Rent Increase',
          type: 'info',
          desc: `12 months from start — earliest a rent increase can take effect`,
        });
      }
    }
  } else {
    // Month-to-month: show rent increase eligibility
    if (province.rentRules.rentIncreaseGuideline) {
      const increaseDate = new Date(start);
      increaseDate.setFullYear(increaseDate.getFullYear() + 1);
      events.push({
        date: increaseDate,
        label: 'Earliest Rent Increase',
        type: 'info',
        desc: '12 months from start',
      });
    }
  }

  // Condition report deadline (BC)
  if (province.code === 'BC') {
    const condDate = new Date(start);
    events.push({
      date: condDate,
      label: 'Condition Inspection',
      type: 'warning',
      desc: 'MANDATORY — must be completed at or before move-in',
    });
  }

  // Sort by date
  events.sort((a, b) => a.date - b.date);

  return renderTimeline(events);
}

function getMonthsDiff(d1, d2) {
  return (d2.getFullYear() - d1.getFullYear()) * 12 + (d2.getMonth() - d1.getMonth());
}

function renderTimeline(events) {
  if (!events.length) return '';

  const fmt = (d) => d.toLocaleDateString('en-CA', { year: 'numeric', month: 'short', day: 'numeric' });

  return `
    <div class="timeline print-page-group">
      <h3 class="timeline-title">Lease Timeline</h3>
      <div class="timeline-track">
        ${events.map(e => `
          <div class="timeline-event timeline-${e.type} print-page-group">
            <div class="timeline-dot"></div>
            <div class="timeline-content">
              <div class="timeline-date">${fmt(e.date)}</div>
              <div class="timeline-label">${e.label}</div>
              <div class="timeline-desc">${e.desc}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}
