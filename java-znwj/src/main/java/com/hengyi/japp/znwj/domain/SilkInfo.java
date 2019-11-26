package com.hengyi.japp.znwj.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.github.ixtf.japp.core.J;
import com.hengyi.japp.znwj.interfaces.python.DetectResult;
import lombok.Data;
import lombok.ToString;

import java.io.Serializable;
import java.util.Collection;
import java.util.Date;

/**
 * @author jzb 2019-11-20
 */
@Data
@ToString(onlyExplicitlyIncluded = true)
public class SilkInfo implements Serializable {
    private String id;
    @ToString.Include
    private String code;
    private int rfidNum;
    private String lineName;
    private int lineMachineItem;
    private int spindle;
    private String batchNo;
    private String batchSpec;
    private Collection<DetectExceptionInfo> detectExceptionInfos;
    private Collection<MesAutoExceptionInfo> mesAutoExceptionInfos;
    private boolean eliminateHandled;
    private Date buildDateTime;
    private Date endDateTime;

    synchronized public void add(DetectResult detectResult) {
        detectExceptionInfos = detectResult.getDetectExceptionInfos();
        endDateTime = new Date();
    }

    public boolean hasException() {
        return hasMesAutoException() || hasDetectException();
    }

    @JsonIgnore
    public boolean hasMesAutoException() {
        return J.emptyIfNull(mesAutoExceptionInfos).parallelStream()
                .map(MesAutoExceptionInfo::hasException)
                .findFirst()
                .isPresent();
    }

    @JsonIgnore
    public boolean hasDetectException() {
        return J.emptyIfNull(detectExceptionInfos)
                .parallelStream()
                .map(DetectExceptionInfo::hasException)
                .findFirst()
                .isPresent();
    }
}
