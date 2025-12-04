
function toggleRexCommitteeFormVisibility() {
    const isitREXField = document.getElementById('IsitREX');
    const showFields = isitREXField.value === 'Yes';
    const fieldGroups = document.querySelectorAll('.dependent-field-group');
    fieldGroups.forEach(group => {
        if (showFields) { group.style.display = ''; } else { group.style.display = 'none'; }
    });
}

function toggleActionFormVisibility() {
    const Isfurtheranalysisrequired = document.getElementById('Isfurtheranalysisrequired');
    const showFields = Isfurtheranalysisrequired.value === 'Required';
    const isRequireVisiblefieldGroups = document.querySelectorAll('.isRequireVisible');
    const isNotRequireVisiblefieldGroups = document.querySelectorAll('.isNotRequireVisible');

    isRequireVisiblefieldGroups.forEach(group => {
        if (showFields) { group.style.display = ''; } else { group.style.display = 'none'; }
    });

    isNotRequireVisiblefieldGroups.forEach(group => {
        if (showFields) { group.style.display = 'none'; } else { group.style.display = ''; }
    });
}

// Call the function on page load to set the initial state correctly
document.addEventListener('DOMContentLoaded', (event) => {
    toggleRexCommitteeFormVisibility();
    toggleActionFormVisibility()
});