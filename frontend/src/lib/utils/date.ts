import dayjs from 'dayjs'

type WithDate = {
  date: string
}
export type DateRangeKey = 'ytd' | '1y' | '2y' | '3y' | '4y' | '5y' | '6y' | '7y' | '8y' | '9y' | '10y' | 'max'

export function getOldestDateISO<T extends WithDate>(
  data: T[]
): string | null {
  if (!data.length) return null

  let oldest = data[0]
  let oldestTs = dayjs(oldest.date).valueOf()

  for (let i = 1; i < data.length; i++) {
    const ts = dayjs(data[i].date).valueOf()
    if (ts < oldestTs) {
      oldest = data[i]
      oldestTs = ts
    }
  }

  return oldest.date
}


export function getDateFromRange(range: DateRangeKey): dayjs.Dayjs {
  const today = dayjs()
  switch (range) {
    case 'ytd':
      return today.startOf('year')
    case '1y':
      return today.subtract(1, 'year')
    case '2y':
      return today.subtract(2, 'year')
    case '3y':
      return today.subtract(3, 'year')
    case '4y':
      return today.subtract(4, 'year')
    case '5y':
      return today.subtract(5, 'year')
    case 'max':
    default:
      return dayjs('1900-01-01')
  }
}

