import React from 'react';
import {
  ScrollView,
  View,
  StyleSheet,
  ViewStyle,
  StyleProp,
  useWindowDimensions,
} from 'react-native';
import { spacing } from '../../theme';

type Props = {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  contentContainerStyle?: StyleProp<ViewStyle>;
};

export const HorizontalRow: React.FC<Props> = ({ children, style, contentContainerStyle }) => {
  const { width: windowWidth } = useWindowDimensions();

  // Card width: show ~2.5 cards so 3rd is peeking (encourages scrolling)
  const cardWidth = Math.min(Math.max(windowWidth * 0.65, 220), 340);

  return (
    <ScrollView
      horizontal
      showsHorizontalScrollIndicator={false}
      style={[styles.scroll, style]}
      contentContainerStyle={[
        styles.content,
        { gap: spacing.md },
        contentContainerStyle,
      ]}
      directionalLockEnabled
      nestedScrollEnabled
    >
      {React.Children.map(children, (child) => (
        <View style={[styles.cardWrapper, { minWidth: cardWidth, maxWidth: cardWidth }]}>
          {child}
        </View>
      ))}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  scroll: {
    flexGrow: 0,
  } as ViewStyle,
  content: {
    paddingRight: spacing.screenPadding,
  } as ViewStyle,
  cardWrapper: {
    marginLeft: spacing.screenPadding,
  } as ViewStyle,
});
