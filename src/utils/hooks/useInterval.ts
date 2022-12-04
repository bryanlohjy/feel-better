import { useEffect } from "react"

const useInterval = (fn: CallableFunction, intervalMs: number) => {
  useEffect(() => {
    const interval = setInterval(fn, intervalMs)
    return () => {
      clearInterval(interval)
    }
   }, [fn, intervalMs])
}

export default useInterval;