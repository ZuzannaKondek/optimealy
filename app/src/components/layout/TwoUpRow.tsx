import React from 'react';
import {
  View,
  StyleSheet,
  ViewStyle,
  StyleProp,
  useWindowDimensions,
} from 'react-native';
import { spacing } from '../../theme';

const MIN_CARD_WIDTH = 160;
const GAP = spacing.md;

type Props = {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
};

export const TwoUpRow: React.FC<Props> = ({ children, style }) => {
  const { width: windowWidth } = useWindowDimensions();

  const isTwoUp = windowWidth >= MIN_CARD_WIDTH * 2 + GAP + spacing.screenPadding * 2;

  return (
    <View style={[styles.container, style]}>
      <View style={isTwoUp ? styles.row : styles.column}>
        {React.Children.map(children, (child, index) => (
          <View
            key={index}
            style={[
              isTwoUp ? styles.halfWidth : styles.fullWidth,
              index === 0 && styles.firstItem,
            ]}
          >
            {child}
          </View>
        ))}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
  } as ViewStyle,
  row: {
    flexDirection: 'row',
    gap: spacing.md,
    alignItems: 'flex-start',
  } as ViewStyle,
  column: {
    flexDirection: 'column',
    gap: spacing.md,
  } as ViewStyle,
  halfWidth: {
    flex: 1,
    minHeight: 210,
  } as ViewStyle,
  fullWidth: {
    width: '100%',
    minHeight: 210,
  } as ViewStyle,
  firstItem: {
    marginBottom: spacing.md,
  } as ViewStyle,
});
