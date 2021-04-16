export const att = (s: string, b?: boolean): any => {
  if (b !== undefined && b === false) return {};
  return { [s]: '' };
};

export const contains = (...y: any): boolean => {
  for (let x of y)
    if (
      x === undefined ||
      x === null ||
      x === '' ||
      x.length === 0 ||
      (typeof x === 'number' && isNaN(x))
    )
      return false;
  return true;
};

export const toTimeblock = (d: Date): Number | Date => {
  if (!contains(d)) return 0; // d === "Invalid Date"
  return d.getDay() * 48 + d.getHours() * 2 + (d.getMinutes() === 0 ? 0 : 1);
};

export const getValidDate = (x: Date): Date => {
  x.setMilliseconds(0);
  x.setSeconds(0);
  x.setMinutes(x.getMinutes() >= 30 ? 30 : 0);
  return x;
};

export const getDateSS = (t: Date): string => {
  return new Date(t.toString().split('GMT')[0] + ' UTC')
    .toISOString()
    .split('.')[0];
};

export const toPythonDate = (d: Date): string => {
  return d.toISOString();
};

export const dateToBackend = (d: Date): string => {
  let month = `${d.getMonth() + 1}`;
  if (month.length === 1) month = '0' + month;
  let date = `${d.getDate()}`;
  if (date.length === 1) date = '0' + date;
  return `${d.getFullYear()}-${month}-${date}T${d.getHours()}:${d.getMinutes()}:${d.getSeconds()}.${d
    .getMilliseconds()
    .toString()}`;
};

export const dateFromBackend = (d: string): Date => {
  return new Date(Date.parse(d.split('.')[0]));
};

export const makeid = (l: number = 15): string => {
  let r: string = '',
    c: string =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  for (let i = 0; i < l; i++)
    r += c.charAt(Math.floor(Math.random() * c.length));
  return r;
};

// handles display of date/time info
export const parseDateTime = (date1: Date, date2: Date): string => {
  let str = date1.toLocaleDateString('en-GB');
  if (
    date1.getMonth() === date2.getMonth() &&
    date1.getDate() === date2.getDate() &&
    date1.getFullYear() === date2.getFullYear()
  ) {
    //if the request starts and ends on the same day
    str =
      str +
      ' ' +
      date1.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
      }) +
      ' - ' +
      date2.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
      });
  } else {
    str =
      str +
      ' ' +
      date1.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
      }) +
      ' - ' +
      date2.toLocaleDateString('en-GB') +
      ' ' +
      date2.toLocaleTimeString('en-US', {
        hour12: true,
        hour: 'numeric',
        minute: 'numeric',
      });
  }
  return str.toLowerCase();
};

export const parseRolesAsString = (list: string[]): string => {
  let s: string = '';
  for (const l of list) {
    s += toSentenceCase(l) + '/';
  }
  return s.slice(0, -1);
};

export const isAvailable = (
  availability: { startTime: Date; endTime: Date }[],
  shift: { startTime: Date; endTime: Date }
): boolean => {
  for (let i = 0; i < availability.length; i++) {
    if (
      availability[i].startTime <= shift.startTime &&
      availability[i].endTime >= shift.endTime
    ) {
      return true;
    }
  }
  return false;
};

export const toSentenceCase = (camelCase: string): string => {
  var result = camelCase.replace(/([A-Z])/g, ' $1');
  var finalResult = result.charAt(0).toUpperCase() + result.slice(1);
  return finalResult;
};
