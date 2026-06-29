import {
    Document,
    Page,
    Text,
    View,
    StyleSheet,
} from '@react-pdf/renderer'

export interface ChordPlacement {
    string: number
    fret: number
}

export interface TabNote {
    type?: 'note' | 'rest' | 'chord'
    measure: number
    string: number | null
    fret: number | null
    pitch?: string
    duration: number
    flag: string | null
    midi: number | null
    octave: number | null
    placements?: ChordPlacement[]
}

export interface TabData {
    tab: TabNote[]
}

interface TabDocumentProps {
    tabData: TabData
}

interface MeasureBlock {
    measureNumber: number
    notes: TabNote[]
    width: number
}

interface SystemRow {
    measures: MeasureBlock[]
    width: number
}

const STRING_LABELS = ['e', 'B', 'G', 'D', 'A', 'E']
const STRING_COUNT = 6
const BEAT_WIDTH = 24
const LABEL_COL_WIDTH = 24
const STRING_ROW_HEIGHT = 18
const PAGE_WIDTH = 515
const AVAILABLE_WIDTH = PAGE_WIDTH - LABEL_COL_WIDTH
const BARLINE_WIDTH = 2
const SYSTEM_MARGIN = 24
const MEASURE_NUMBER_HEIGHT = 14
const SYSTEM_HEIGHT =
    MEASURE_NUMBER_HEIGHT + STRING_COUNT * STRING_ROW_HEIGHT + SYSTEM_MARGIN
const PAGE_HEIGHT = 842
const PAGE_PADDING = 80
const TITLE_HEIGHT = 46

const styles = StyleSheet.create({
    page: {
        padding: 40,
        fontFamily: 'Helvetica',
    },
    title: {
        fontSize: 22,
        fontWeight: 'bold',
        marginBottom: 24,
        textAlign: 'center',
    },
    system: {
        marginBottom: SYSTEM_MARGIN,
    },
    measureNumberRow: {
        flexDirection: 'row',
        height: MEASURE_NUMBER_HEIGHT,
        alignItems: 'flex-end',
    },
    measureNumberSpacer: {
        width: LABEL_COL_WIDTH,
    },
    measureNumberCell: {
        justifyContent: 'flex-end',
    },
    measureNumberText: {
        fontSize: 9,
        color: '#444',
    },
    stringRow: {
        flexDirection: 'row',
        alignItems: 'center',
        height: STRING_ROW_HEIGHT,
        borderBottomWidth: 1,
        borderBottomColor: '#333',
    },
    stringLabel: {
        width: LABEL_COL_WIDTH,
        fontSize: 10,
        fontWeight: 'bold',
        textAlign: 'right',
        paddingRight: 6,
    },
    measuresRow: {
        flexDirection: 'row',
        alignItems: 'stretch',
    },
    measureContainer: {
        flexDirection: 'row',
        borderRightWidth: BARLINE_WIDTH,
        borderRightColor: '#333',
    },
    measureContainerLast: {
        flexDirection: 'row',
        borderRightWidth: BARLINE_WIDTH * 2,
        borderRightColor: '#333',
    },
    noteCell: {
        alignItems: 'center',
        justifyContent: 'center',
        height: STRING_ROW_HEIGHT,
    },
    fretText: {
        fontSize: 10,
        fontWeight: 'bold',
    },
    dashText: {
        fontSize: 10,
        color: '#666',
    },
})

function noteCellWidth(duration: number): number {
    return Math.max(duration * BEAT_WIDTH, BEAT_WIDTH * 0.5)
}

function measureWidth(notes: TabNote[]): number {
    return notes.reduce((total, note) => total + noteCellWidth(note.duration), 0)
}

function groupNotesByMeasure(notes: TabNote[]): MeasureBlock[] {
    const grouped = new Map<number, TabNote[]>()

    for (const note of notes) {
        const measureNotes = grouped.get(note.measure) ?? []
        measureNotes.push(note)
        grouped.set(note.measure, measureNotes)
    }

    return [...grouped.entries()]
        .sort(([a], [b]) => a - b)
        .map(([measureNumber, measureNotes]) => ({
            measureNumber,
            notes: measureNotes,
            width: measureWidth(measureNotes),
        }))
}

function packMeasuresIntoSystems(measures: MeasureBlock[]): SystemRow[] {
    const systems: SystemRow[] = []
    let currentMeasures: MeasureBlock[] = []
    let currentWidth = 0

    for (const measure of measures) {
        const wouldOverflow =
            currentMeasures.length > 0 &&
            currentWidth + measure.width > AVAILABLE_WIDTH

        if (wouldOverflow) {
            systems.push({
                measures: currentMeasures,
                width: currentWidth,
            })
            currentMeasures = []
            currentWidth = 0
        }

        currentMeasures.push(measure)
        currentWidth += measure.width
    }

    if (currentMeasures.length > 0) {
        systems.push({
            measures: currentMeasures,
            width: currentWidth,
        })
    }

    return systems
}

function packSystemsIntoPages(systems: SystemRow[]): SystemRow[][] {
    const pages: SystemRow[][] = []
    let currentPage: SystemRow[] = []
    let usedHeight = TITLE_HEIGHT

    for (const system of systems) {
        const nextHeight = usedHeight + SYSTEM_HEIGHT
        const maxHeight = PAGE_HEIGHT - PAGE_PADDING

        if (currentPage.length > 0 && nextHeight > maxHeight) {
            pages.push(currentPage)
            currentPage = []
            usedHeight = 0
        }

        currentPage.push(system)
        usedHeight += SYSTEM_HEIGHT
    }

    if (currentPage.length > 0) {
        pages.push(currentPage)
    }

    return pages.length > 0 ? pages : [[]]
}

function backendStringForRow(rowIndex: number): number {
    return STRING_COUNT - rowIndex
}

function getCellContent(note: TabNote, backendString: number): string {
    const noteType = note.type ?? (note.flag === 'rest' ? 'rest' : 'note')

    if (noteType === 'rest' || note.flag === 'rest') {
        return backendString === STRING_COUNT ? 'r' : '—'
    }

    if (note.flag === 'out_of_range') {
        return backendString === 1 ? '?' : '—'
    }

    if (noteType === 'chord' && note.placements) {
        const placement = note.placements.find((p) => p.string === backendString)
        return placement !== undefined ? String(placement.fret) : '—'
    }

    if (note.string === backendString && note.fret !== null) {
        return String(note.fret)
    }

    return '—'
}

function TabSystem({
    system,
    isLastSystem,
}: {
    system: SystemRow
    isLastSystem: boolean
}) {
    return (
        <View style={styles.system}>
            <View style={styles.measureNumberRow}>
                <View style={styles.measureNumberSpacer} />
                {system.measures.map((measure) => (
                    <View
                        key={`num-${measure.measureNumber}`}
                        style={[styles.measureNumberCell, { width: measure.width }]}
                    >
                        <Text style={styles.measureNumberText}>
                            {measure.measureNumber}
                        </Text>
                    </View>
                ))}
            </View>

            {STRING_LABELS.map((label, rowIndex) => {
                const backendString = backendStringForRow(rowIndex)

                return (
                    <View key={label} style={styles.stringRow}>
                        <Text style={styles.stringLabel}>{label}</Text>
                        <View style={styles.measuresRow}>
                            {system.measures.map((measure, measureIndex) => {
                                const isLastMeasure =
                                    isLastSystem &&
                                    measureIndex === system.measures.length - 1

                                return (
                                    <View
                                        key={`${measure.measureNumber}-${label}`}
                                        style={
                                            isLastMeasure
                                                ? styles.measureContainerLast
                                                : styles.measureContainer
                                        }
                                    >
                                        {measure.notes.map((note, noteIndex) => {
                                            const content = getCellContent(
                                                note,
                                                backendString,
                                            )
                                            const isFret =
                                                content !== '—' && content !== 'r'

                                            return (
                                                <View
                                                    key={`${noteIndex}-${backendString}`}
                                                    style={[
                                                        styles.noteCell,
                                                        {
                                                            width: noteCellWidth(
                                                                note.duration,
                                                            ),
                                                        },
                                                    ]}
                                                >
                                                    <Text
                                                        style={
                                                            isFret
                                                                ? styles.fretText
                                                                : styles.dashText
                                                        }
                                                    >
                                                        {content}
                                                    </Text>
                                                </View>
                                            )
                                        })}
                                    </View>
                                )
                            })}
                        </View>
                    </View>
                )
            })}
        </View>
    )
}

export default function TabDocument({ tabData }: TabDocumentProps) {
    const measures = groupNotesByMeasure(tabData.tab ?? [])
    const systems = packMeasuresIntoSystems(measures)
    const pages = packSystemsIntoPages(systems)

    let systemOffset = 0
    const pagesWithIndices = pages.map((pageSystems) => {
        const startIndex = systemOffset
        systemOffset += pageSystems.length
        return { pageSystems, startIndex }
    })

    return (
        <Document>
            {pagesWithIndices.map(({ pageSystems, startIndex }, pageIndex) => (
                <Page key={`page-${pageIndex}`} size="A4" style={styles.page}>
                    {pageIndex === 0 && (
                        <Text style={styles.title}>Guitar Tabs</Text>
                    )}
                    {pageSystems.map((system, indexOnPage) => {
                        const globalIndex = startIndex + indexOnPage
                        const isLastSystem = globalIndex === systems.length - 1

                        return (
                            <TabSystem
                                key={`system-${globalIndex}`}
                                system={system}
                                isLastSystem={isLastSystem}
                            />
                        )
                    })}
                </Page>
            ))}
        </Document>
    )
}
