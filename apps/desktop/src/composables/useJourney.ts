import { computed, ref, watch } from 'vue'

export type JourneyStep = 'prepare' | 'scan' | 'naming' | 'execute' | 'postprocess' | 'archive'
export type UtilityPage = 'settings' | 'safety' | null

const journeyOrder: JourneyStep[] = ['prepare', 'scan', 'naming', 'execute', 'postprocess', 'archive']

const activeStep = ref<JourneyStep>('prepare')
const utilityPage = ref<UtilityPage>(null)
const projectRoot = ref('')
const scanResult = ref<any>(null)
const renamePlan = ref<any>(null)
const postprocessDone = ref(false)

const isUtilityPage = computed(() => utilityPage.value !== null)
const currentStepIndex = computed(() => journeyOrder.indexOf(activeStep.value))
const isFirstStep = computed(() => currentStepIndex.value === 0)
const isLastStep = computed(() => currentStepIndex.value === journeyOrder.length - 1)
const currentStepNumber = computed(() => currentStepIndex.value + 1)

function goToStep(step: JourneyStep) {
  activeStep.value = step
  if (utilityPage.value) utilityPage.value = null
}

function goToNext() {
  const idx = journeyOrder.indexOf(activeStep.value)
  if (idx < journeyOrder.length - 1) {
    activeStep.value = journeyOrder[idx + 1]
  }
}

function goToPrev() {
  const idx = journeyOrder.indexOf(activeStep.value)
  if (idx > 0) {
    activeStep.value = journeyOrder[idx - 1]
  }
}

function openUtility(page: UtilityPage) {
  utilityPage.value = page
}

function closeUtility() {
  utilityPage.value = null
}

function setProjectRoot(path: string) {
  projectRoot.value = path
  scanResult.value = null
  renamePlan.value = null
  postprocessDone.value = false
}

// Persist theme
const theme = ref(localStorage.getItem('photograph-workflow-theme') || 'cobalt')

watch(theme, (val) => {
  document.documentElement.dataset.theme = val
  localStorage.setItem('photograph-workflow-theme', val)
}, { immediate: true })

export function useJourney() {
  return {
    // State
    activeStep,
    utilityPage,
    projectRoot,
    scanResult,
    renamePlan,
    postprocessDone,
    theme,
    journeyOrder,

    // Computed
    isUtilityPage,
    currentStepIndex,
    isFirstStep,
    isLastStep,
    currentStepNumber,

    // Actions
    goToStep,
    goToNext,
    goToPrev,
    openUtility,
    closeUtility,
    setProjectRoot,
  }
}
