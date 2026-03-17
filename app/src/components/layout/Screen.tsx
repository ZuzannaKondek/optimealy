import React from 'react';
import { ScrollView, View, ViewStyle, StyleProp } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { colors, spacing } from '../../theme';

type Props = {
  children: React.ReactNode;
  scroll?: boolean;
  style?: StyleProp<ViewStyle>;
  contentContainerStyle?: StyleProp<ViewStyle>;
};

export const Screen: React.FC<Props> = ({
  children,
  scroll = true,
  style,
  contentContainerStyle,
}) => {
  if (scroll) {
    return (
      <SafeAreaView style={[styles.container, style]} edges={['left', 'right']}>
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={[styles.content, contentContainerStyle]}
          showsVerticalScrollIndicator={false}
        >
          {children}
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={[styles.container, style]} edges={['left', 'right']}>
      <View style={[styles.content, contentContainerStyle]}>
        {children}
      </View>
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
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.lg,
  } as ViewStyle,
};
