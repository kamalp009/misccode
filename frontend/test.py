function jsonToReadable(obj, indent = 0) {
  let output = "";
  const spaces = " ".repeat(indent);

  // Function to find step number field dynamically
  function findStepNumberField(item) {
    if (typeof item !== "object" || item === null) return null;
    
    // Common variations of step number field names
    const stepFieldVariations = [
      'step_number', 'step number', 'stepnumber', 'step_no', 'step no', 
      'step', 'step_id', 'stepid', 'number', 'no', 'sequence', 'order'
    ];
    
    for (let key in item) {
      if (stepFieldVariations.includes(key.toLowerCase().replace(/[_\s]/g, '').replace(/[_\s]/g, ' ').trim().toLowerCase())) {
        return key;
      }
    }
    return null;
  }

  // Iterate over all keys in the object
  for (let key in obj) {
    if (!obj.hasOwnProperty(key)) continue;

    const value = obj[key];
    const formattedKey = key.replace(/_/g, " "); // Optional: Replace underscores with spaces

    if (Array.isArray(value)) {
      // If it's an array, print each element recursively
      output += `${spaces}${formattedKey}:\n\n`;
      value.forEach((item, index) => {
        // Dynamically find step number field
        const stepField = findStepNumberField(item);
        
        if (stepField && item[stepField]) {
          output += `${spaces}  Step ${item[stepField]}:\n`;
          // Create a copy of the item without the step number field to avoid duplication
          const itemCopy = { ...item };
          delete itemCopy[stepField];
          output += jsonToReadable(itemCopy, indent + 4);
        } else {
          output += `${spaces}  ${index + 1}:\n`;
          output += jsonToReadable(item, indent + 4);
        }
        output += "\n"; // Add extra line break between steps
      });
    } else if (typeof value === "object" && value !== null) {
      // If it's a nested object, recurse into it
      output += `${spaces}${formattedKey}:\n\n`;
      output += jsonToReadable(value, indent + 2);
    } else {
      // Normal key-value
      output += `${spaces}${formattedKey}: ${value}\n\n`;
    }
  }

  return output;
}
