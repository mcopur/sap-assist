import React from 'react';
import { Chip, Box, Typography } from '@mui/material';

interface SuggestionChipsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
}

const SuggestionChips: React.FC<SuggestionChipsProps> = ({ suggestions, onSuggestionClick }) => {
  return (
    <Box sx={{ my: 2 }}>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Suggested Actions:</Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {suggestions.map((suggestion, index) => (
          <Chip
            key={index}
            label={suggestion}
            onClick={() => onSuggestionClick(suggestion)}
            variant="outlined"
            color="primary"
            sx={{ 
              '&:hover': { 
                backgroundColor: 'primary.light',
                color: 'primary.contrastText'
              }
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export default SuggestionChips;