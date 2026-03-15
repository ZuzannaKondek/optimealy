import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, ActivityIndicator, TouchableOpacity, Alert } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';
import { usePlans } from '../../hooks/usePlans';
import { DayCard } from '../../components/plan/DayCard';
import { colors, spacing, typography } from '../../theme';
import { planService } from '../../services/planService';

type RouteParams = {
  planId: string;
};

export const PlanDetailScreen: React.FC = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { planId } = (route.params as RouteParams) ?? {};

  const { selectedPlan, isLoadingDetail, error, fetchPlanDetail, fetchPlans, setSelectedPlan } = usePlans();
  const [isActivating, setIsActivating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleActivatePlan = async () => {
    try {
      setIsActivating(true);
      const updatedPlan = await planService.activatePlan(planId);
      // Update local state immediately so button disappears right away
      setSelectedPlan(updatedPlan);
      Alert.alert(
        'Plan aktywny! 🎉',
        'Twój plan posiłków jest teraz aktywny. Wszystkie produkty zostały dodane do Twojej spiżarni.',
        [
          {
            text: 'Zobacz dzisiaj',
            onPress: () => navigation.navigate('Today' as never),
          },
          {
            text: 'OK',
            style: 'cancel',
          },
        ]
      );
      // Also refresh from server to ensure consistency
      await fetchPlanDetail(planId);
    } catch (err: any) {
      Alert.alert(
        'Błąd',
        err.response?.data?.detail || 'Nie udało się aktywować planu'
      );
    } finally {
      setIsActivating(false);
    }
  };

  const handleDeletePlan = () => {
    console.log('Opening delete confirmation');
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    console.log('Delete confirmed, planId:', planId);
    setShowDeleteConfirm(false);
    try {
      setIsDeleting(true);
      console.log('Calling deletePlan...');
      await planService.deletePlan(planId);
      console.log('Delete successful');
      // Refresh plans list first, then navigate
      await fetchPlans();
      console.log('Navigating to HomeMain');
      navigation.navigate('HomeMain' as never);
    } catch (err: any) {
      console.log('Delete error:', err);
      setIsDeleting(false);
    }
  };

  React.useEffect(() => {
    if (planId) void fetchPlanDetail(planId);
  }, [fetchPlanDetail, planId]);

  if (!planId) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Brak planId</Text>
      </View>
    );
  }

  if (isLoadingDetail || !selectedPlan || selectedPlan.plan_id !== planId) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Ładowanie planu…</Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>
        {selectedPlan.name || `${selectedPlan.start_date} • ${selectedPlan.duration_days} dni`}
      </Text>

      <View style={styles.metrics}>
        <Text style={styles.metric}>Cel: {selectedPlan.target_calories_per_day} kcal/dzień</Text>
        {selectedPlan.estimated_food_waste_g != null ? (
          <Text style={styles.metric}>Odpady: {Math.round(selectedPlan.estimated_food_waste_g)}g</Text>
        ) : null}
        {selectedPlan.waste_reduction_percentage != null ? (
          <Text style={styles.metric}>Redukcja odpadów: {selectedPlan.waste_reduction_percentage}%</Text>
        ) : null}

        <TouchableOpacity
          style={styles.groceryButton}
          onPress={() => navigation.navigate('GroceryList' as never, { planId: selectedPlan.plan_id } as never)}
        >
          <Text style={styles.groceryButtonText}>Potrzebne produkty</Text>
        </TouchableOpacity>

        {selectedPlan.execution_status === 'draft' && (
          <TouchableOpacity
            style={[styles.activateButton, isActivating && styles.buttonDisabled]}
            onPress={handleActivatePlan}
            disabled={isActivating}
          >
            <Text style={styles.activateButtonText}>
              {isActivating ? 'Aktywacja...' : 'Kup produkty i rozpocznij plan'}
            </Text>
          </TouchableOpacity>
        )}

        {(selectedPlan.execution_status === 'completed' || selectedPlan.execution_status === 'cancelled') && (
          <View style={styles.statusBadge}>
            <Text style={styles.statusBadgeText}>
              {selectedPlan.execution_status === 'completed' ? '✓ Zakończony' : '✕ Anulowany'}
            </Text>
          </View>
        )}
      </View>

      {/* Delete Plan Button - works for all statuses */}
      <TouchableOpacity
        style={[styles.deleteButton, isDeleting && styles.buttonDisabled]}
        onPress={() => {
          console.log('Delete button pressed');
          handleDeletePlan();
        }}
        disabled={isDeleting}
      >
        <Text style={styles.deleteButtonText}>
          {isDeleting ? 'Usuwanie...' : 'Usuń plan'}
        </Text>
      </TouchableOpacity>

      <Text style={styles.sectionTitle}>Dni</Text>
      {selectedPlan.daily_menus.map((day) => (
        <DayCard
          key={`${selectedPlan.plan_id}-${day.day_number}`}
          day={day}
          onPress={() =>
            navigation.navigate(
              'DayDetail' as never,
              { planId: selectedPlan.plan_id, dayNumber: day.day_number } as never
            )
          }
        />
      ))}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Usunąć plan?</Text>
            <Text style={styles.modalText}>Ta operacja jest nieodwracalna. Plan zostanie trwale usunięty.</Text>
            <View style={styles.modalButtons}>
              <TouchableOpacity
                style={styles.modalCancelButton}
                onPress={() => setShowDeleteConfirm(false)}
              >
                <Text style={styles.modalCancelText}>Anuluj</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalDeleteButton}
                onPress={confirmDelete}
              >
                <Text style={styles.modalDeleteText}>Usuń</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    padding: spacing.screenPadding,
    paddingBottom: spacing.lg,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.background,
    padding: spacing.lg,
  },
  loadingText: {
    marginTop: spacing.sm,
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  metrics: {
    backgroundColor: colors.surface,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: spacing.borderRadius,
    padding: spacing.md,
    marginBottom: spacing.lg,
    gap: spacing.xs,
  },
  metric: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  groceryButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.primary,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.sm,
    alignItems: 'center',
  },
  groceryButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  activateButton: {
    marginTop: spacing.sm,
    backgroundColor: colors.success,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.md,
    alignItems: 'center',
  },
  activateButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.bold,
  },
  buttonDisabled: {
    opacity: 0.5,
  },
  statusBadge: {
    marginTop: spacing.sm,
    padding: spacing.sm,
    backgroundColor: colors.backgroundSecondary,
    borderRadius: spacing.borderRadius,
    alignItems: 'center',
  },
  statusBadgeText: {
    color: colors.textSecondary,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.semiBold,
  },
  deleteButton: {
    marginTop: spacing.lg,
    backgroundColor: colors.error,
    borderRadius: spacing.borderRadius,
    paddingVertical: spacing.md,
    alignItems: 'center',
    marginBottom: spacing.lg,
  },
  deleteButtonText: {
    color: colors.white,
    fontSize: typography.fontSize.md,
    fontWeight: typography.fontWeight.bold,
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: typography.fontWeight.semiBold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  errorText: {
    color: colors.error,
    textAlign: 'center',
  },
  // Delete confirmation modal
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.lg,
  },
  modalContent: {
    backgroundColor: colors.surface,
    borderRadius: spacing.borderRadius,
    padding: spacing.lg,
    width: '100%',
    maxWidth: 320,
  },
  modalTitle: {
    fontSize: typography.fontSize.xl,
    fontWeight: typography.fontWeight.bold,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  modalText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  modalButtons: {
    flexDirection: 'row',
    gap: spacing.md,
    justifyContent: 'center',
  },
  modalCancelButton: {
    flex: 1,
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
  },
  modalCancelText: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    fontWeight: typography.fontWeight.medium,
  },
  modalDeleteButton: {
    flex: 1,
    padding: spacing.md,
    borderRadius: spacing.borderRadius,
    backgroundColor: colors.error,
    alignItems: 'center',
  },
  modalDeleteText: {
    fontSize: typography.fontSize.md,
    color: colors.white,
    fontWeight: typography.fontWeight.semiBold,
  },
});
