import React from 'react';
import { ScrollView, View, ViewStyle, StyleProp, useWindowDimensions } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, spacing } from '../../theme';

type Props = {
  children: React.ReactNode;
  scroll?: boolean;
  horizontal?: boolean;
  wide?: boolean;
  style?: StyleProp<ViewStyle>;
  contentContainerStyle?: StyleProp<ViewStyle>;
  refreshControl?: React.ReactElement;
};

export const Screen: React.FC<Props> = ({
  children,
  scroll = true,
  horizontal = false,
  wide = false,
  style,
  contentContainerStyle,
  refreshControl,
}) => {
  const { width } = useWindowDimensions();
  const isWide = wide || width >= 768;

  if (!scroll) {
    // No scroll - content flows naturally
    return (
      <SafeAreaView style={[styles.container, style]} edges={['left', 'right']}>
        <View style={[styles.content, contentContainerStyle]}>
          {children}
        </View>
      </SafeAreaView>
    );
  }

  if (horizontal) {
    // Explicit horizontal scroll
    return (
      <SafeAreaView style={[styles.container, style]} edges={['left', 'right']}>
        <ScrollView
          style={styles.horizontalScroll}
          contentContainerStyle={[styles.content, contentContainerStyle]}
          showsHorizontalScrollIndicator={true}
          refreshControl={refreshControl}
          nestedScrollEnabled={true}
          horizontal={true}
        >
          {children}
        </ScrollView>
      </SafeAreaView>
    );
  }

  // Vertical scroll - with special handling for wide screens
  return (
    <SafeAreaView style={[styles.container, style]} edges={['left', 'right']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[styles.content, contentContainerStyle]}
        showsVerticalScrollIndicator={!isWide}
        refreshControl={refreshControl}
        nestedScrollEnabled={true}
        // On wide screens, don't lock to vertical so horizontal scroll can work inside
        directionalLockEnabled={!isWide}
      >
        {children}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = {
  container: {
    flex: 1,
    backgroundColor: colors.background,
  } as ViewStyle,
  scroll: {
    flex: 1,
  } as ViewStyle,
  horizontalScroll: {
    flex: 1,
    flexDirection: 'row',
  } as ViewStyle,
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.lg,
  } as ViewStyle,
};
