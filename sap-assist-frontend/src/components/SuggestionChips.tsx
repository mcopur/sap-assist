import React from 'react';
import { Chip, Box } from '@mui/material';

interface SuggestionChipsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
}

const SuggestionChips: React.FC<SuggestionChipsProps> = ({ suggestions, onSuggestionClick }) => {
  return (
    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, my: 2 }}>
      {suggestions.map((suggestion, index) => (
        <Chip
          key={index}
          label={suggestion}
          onClick={() => onSuggestionClick(suggestion)}
          variant="outlined"
        />
      ))}
    </Box>
  );
};

export default SuggestionChips;