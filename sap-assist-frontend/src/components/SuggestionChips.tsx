import React from 'react';
import { Chip, Box, Typography, useTheme } from '@mui/material';

interface SuggestionChipsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
  isMobile: boolean;
}

const SuggestionChips: React.FC<SuggestionChipsProps> = ({ suggestions, onSuggestionClick, isMobile }) => {
  const theme = useTheme();

  return (
    <Box sx={{ my: 2 }}>
      <Typography variant={isMobile ? "body2" : "subtitle2"} sx={{ mb: 1 }}>Suggested Actions:</Typography>
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 1,
        justifyContent: isMobile ? 'center' : 'flex-start'
      }}>
        {suggestions.map((suggestion, index) => (
          <Chip
            key={index}
            label={suggestion}
            onClick={() => onSuggestionClick(suggestion)}
            variant="outlined"
            color="primary"
            size={isMobile ? "small" : "medium"}
            sx={{ 
              '&:hover': { 
                backgroundColor: 'primary.light',
                color: 'primary.contrastText'
              },
              transition: theme.transitions.create(['background-color', 'color'], {
                duration: theme.transitions.duration.short,
              }),
            }}
          />
        ))}
      </Box>
    </Box>
  );
};

export default SuggestionChips;